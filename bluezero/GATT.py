"""
Classes that represent the GATT features of a remote device.

This file provides a different approach to building the classes and definitions
found in GATT.py
"""

# DBus import for handling DBus objects and interfaces
import dbus

# Mainloop import for stopping the loop in the GATT Manager
import dbus.mainloop.glib
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

# Logging
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Empty Null Handler for the logger."""

        def emit(self, record):
            """Emit function to match default logging behaviour."""
            pass

# Only dependency within the bluezero library is the constants definitions
from bluezero import constants
from bluezero import tools

# Mainloop is used in error callbacks to stop the loop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
mainloop = GObject.MainLoop()

# Initialise the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(NullHandler())


class CommonGATT(tools.DBusObject):
    """Common GATT Object Properties."""

    def __init__(self, obj_path, meth_iface, obj_iface, gatt_parent):
        """
        Call the parent initialisation function and store the object interface.

        :param obj_path: path to the object (service, characteristic, etc.)
        or object UUID (in which case it is combined with obj_iface to find the
        path using uuid_dbus_path from tools)
        :param meth_iface: interface to look for methods on (adapter,
        characteristic, etc.)
        :param obj_iface: dbus interface for the object (service,
        characteristic, etc.)
        :param gatt_parent: name of the GATT parent, e.g. for a Service,
        'Device', a Characteristic, 'Service', etc.
        :type obj_path: dbus path
        :type meth_iface: string (DBus interface descriptor)
        :type obj_iface: string (DBus interface descriptor)
        :type gatt_parent: string
        """
        if '/' not in obj_path:
            try:
                obj_path = tools.uuid_dbus_path(obj_iface, obj_path)[0]
            except Exception as e:
                print('Attempt to get path from UUID failed.  UUID was {0}, '
                      'original error: {1}'.format(obj_path, e))
                raise

        super(CommonGATT, self).__init__(obj_path, meth_iface)
        self.obj_iface = obj_iface
        self.gatt_parent = gatt_parent

    @property
    def UUID(self):
        """
        Return the value of the GATT Object UUID for this path.

        :return: GATT Object UUID, e.g. '00001800-0000-1000-8000-00805f9b34fb'
        :rtype: DBus string
        """
        return self.obj_props.Get(self.obj_iface, 'UUID')

    @property
    def parent(self):
        """
        Return the DBus object that is the GATT parent for this class.

        :return: the GATT parent
        :rtype: DBus ObjectPath
        """
        return self.obj_props.Get(self.obj_iface, self.gatt_parent)


class Service(CommonGATT):
    """Remote GATT Service."""

    def __init__(self, service_path):
        """
        Remote GATT Service Initialisation.

        :param service_path: dbus path to the service.
        :type service_path: string (dbus path)
        """
        super(Service, self).__init__(service_path,
                                      constants.ADAPTER_INTERFACE,
                                      constants.GATT_SERVICE_IFACE,
                                      'Device')

    @property
    def primary(self):
        """
        Indentifier for whether the Service is a primary Service.

        :return: Indentifier
        :rtype: DBus boolean
        """
        return self.obj_props.Get(self.obj_iface, 'Primary')

    def __repr__(self):
        """
        Overload the display operator.

        :return: Service information
        :rtype: string
        """
        strinfo = """GATT Service.
    Path: {}
    Device: {}
    UUID: {}
    Primary: {}""".format(self.obj_path, self.parent,
                          self.UUID, self.primary)
        return strinfo


class CharDesc(CommonGATT):
    """Parent Class for Remote GATT Descriptor or Characteristic."""

    def __init__(self, obj_path, obj_iface, obj_parent):
        """
        Remote GATT Characteristic Initialisation.

        :param obj_path: dbus path to the characteristic/descriptor.
        :type obj_path: string (dbus path)
        """
        super(CharDesc, self).__init__(obj_path, obj_iface, obj_iface,
                                       obj_parent)
        self._value = self.obj_props.Get(self.obj_iface, 'Value')
        self._use_cached = False
        self.rw_flags = {}

    @property
    def value(self):
        """
        The value of the characteristic/descriptor.

        Read/Write attempt to use the DBus methods to get the value.  If the
        _use_cached property is true, this is bypassed and the cached value
        from the DBus properties interface is used.

        When using the DBus ReadValue or WriteValue methods to get or set the
        value, the property `rw_flags` can be used to control the behaviour.

        This should be a dictionary with the following options:
        "offset": Start offset
        "device": Device path (Server only)

        Possible Errors are: org.bluez.Error.Failed
                             org.bluez.Error.InProgress
                             org.bluez.Error.NotPermitted
                             org.bluez.Error.InvalidValueLength
                             org.bluez.Error.NotAuthorized
                             org.bluez.Error.NotSupported

        :return: Characteristic/Descriptor value
        :rtype: DBus Byte Array
        """
        if 'read' not in self.flags:
            logger.info('Read is not available on interface {0} with UUID',
                        '{1}'.format(self.obj_iface, self.UUID))
            return 'N/A'

        if self._use_cached:
            value = self.obj_props.Get(self.obj_iface, 'Value')
        else:
            value = self.obj_methods.ReadValue(dbus.Array(self.rw_flags))

            return value

    @value.setter
    def value(self, value):
        """Set the value of the characteristic/descriptor."""
        if 'write' not in self.flags:
            logger.info('Write is not available on interface {0} with UUID',
                        '{1}'.format(self.obj_iface, self.UUID))

        self.obj_methods.WriteValue(value, dbus.Array(self.rw_flags))

    @property
    def flags(self):
        """
        Return a list of how this characteristic's value can be used.

        :return: list of flags, e.g. example ['read', 'write', 'notify']
        :rtype: DBus Array
        """
        return self.obj_props.Get(self.obj_iface, 'Flags')


class Characteristic(CharDesc):
    """Remote GATT Characteristic."""

    def __init__(self, characteristic_path):
        """
        Remote GATT Characteristic Initialisation.

        :param characteristic_path: dbus path to the characteristic.
        :type characteristic_path: string (dbus path)
        """
        super(Characteristic, self).__init__(characteristic_path,
                                             constants.GATT_CHRC_IFACE,
                                             'Service')
        self._notifying = False
        self._notify_cb = None

    @property
    def notifying(self):
        """
        Enable or disable notifications on this Characteristic.

        :return: notification state
        :rtype: DBus Boolean
        """
        if 'notify' not in self.flags:
            logger.info('Notifications are not available on interface {0} with'
                        'UUID {1}'.format(self.obj_iface, self.UUID))
            return 'N/A'
        return self.obj_props.Get(self.obj_iface, 'Notifying')

    @notifying.setter
    def notifying(self, value):
        """
        Start or stop notifications depending on the notification state.

        :param value: new state of notification
        :type value: boolean
        """
        if 'notify' not in self.flags:
            logger.info('Notifications are not available on interface {0} with'
                        'UUID {1}'.format(self.obj_iface, self.UUID))

        if value:
            if not self.notifying:
                self.obj_methods.StartNotify(
                    reply_handler=self.start_notify_cb,
                    error_handler=tools.generic_error_cb,
                    dbus_interface=constants.GATT_CHRC_IFACE)
                self.obj_props.connect_to_signal('PropertiesChanged',
                                                 self._props_changed_cb)
        else:
            if self.notifying:
                self.obj_methods.StopNotify(
                    reply_handler=self.stop_notify_cb,
                    error_handler=tools.generic_error_cb,
                    dbus_interface=constants.GATT_CHRC_IFACE)

    @property
    def notify_cb(self):
        """
        Callback used when the Characteristic value changes.

        Notifying must be true for the callback to be triggered.

        :param callback: callback function to be added.
        :type callback: function
        """
        return self._notify_cb

    @notify_cb.setter
    def notify_cb(self, callback):
        """
        Setter for the notify callback.

        :param callback: callback function to be added.
        :type callback: function
        """
        self._notify_cb = callback

    def _props_changed_cb(self, iface, changed_props, invalidated_props):
        """
        Callback indicating that properties have changed.

        If notify_cb is not none, it call that function with the value

        :param iface: Interface associated with the callback.
        :param changed_props: Properties changed that triggered the callback.
        :param invalidated_props: Unused.
        :type iface: string (DBus interface)
        :type changed_props: DBus properties interface
        """
        if iface != self.obj_iface or not len(changed_props):
            return

        value = changed_props.get('Value', None)
        if not value:
            return

        logger.debug('Properties changed: ', value)

        if self._notify_cb is not None:
            self._notify_cb(value)

    def start_notify_cb(self):
        """Callback associated with enabling notifications."""
        logger.info('Notifications enabled')

    def stop_notify_cb(self):
        """Callback associated with disabling notifications."""
        logger.info('Notifications disabled')

    def __repr__(self):
        """
        Overload the display operator.

        :return: Characteristic information
        :rtype: string
        """
        strinfo = """GATT Characteristic.
    Path: {}
    Service: {}
    UUID: {}
    Value: {}
    use_cached: {}
    Notifying: {}
    Flags: {}""".format(self.obj_path, self.parent, self.UUID, self.value,
                        self._use_cached, self.notifying, self.flags)
        return strinfo


class Descriptor(CharDesc):
    """Remote GATT Characteristic."""

    def __init__(self, descriptor_path):
        """
        Remote GATT Descriptor Initialisation.

        :param descriptor_path: dbus path to the descriptor.
        :type descriptor_path: string (dbus path)
        """
        super(Descriptor, self).__init__(descriptor_path,
                                         constants.GATT_DESC_IFACE,
                                         'Characteristic')

    def __repr__(self):
        """
        Overload the display operator.

        :return: Descriptor information
        :rtype: string
        """
        strinfo = """GATT Descriptor.
    Path: {}
    Characteristic: {}
    UUID: {}
    Value: {}
    use_cached: {}
    Flags: {}""".format(self.obj_path, self.parent, self.UUID, self.value,
                        self._use_cached, self.flags)
        return strinfo


class Profile(tools.DBusObject):
    """Remote GATT Profile."""

    def __init__(self, profile_path):
        """
        Remote GATT Profile Initialisation.

        :param profile_path: dbus path to the profile.
        :type profile_path: string (dbus path)
        """
        super(Profile, self).__init__(profile_path,
                                      constants.GATT_PROFILE_IFACE)

    def release(self):
        """Release the profile."""
        self.obj_methods.Release()

    @property
    def UUIDs(self):
        """
        128-bit GATT service UUIDs to auto connect.

        :return: list of UUIDs
        :rtype: DBus Array
        """
        return self.obj_props.Get(self.obj_iface, 'UUIDs')


class GattManager(tools.DBusObject):
    """GATT Manager."""

    def __init__(self, manager_path):
        """
        GATT Manager Initialisation.

        :param manager_path: dbus path to the GATT Manager.
        :type manager_path: string (dbus path)
        """
        super(GattManager, self).__init__(manager_path,
                                          constants.GATT_MANAGER_IFACE)

    def register_application(self, application, options):
        """
        Register an application with the GATT Manager.

        :param application: Application object.
        :param options:
        """
        self.manager_methods.RegisterApplication(
            application.get_path(), options,
            reply_handler=self.register_app_cb,
            error_handler=self.register_app_error_cb
        )

    def unregister_application(self, application):
        """
        Unregister an application with the GATT Manager.

        :param application: Application object.
        :return:
        """
        self.obj_methods.UnregisterApplication(application)

        def register_app_cb():
            """Application registration callback."""
            logger.info('GATT application registered')

        def register_app_error_cb(error):
            """Application registration error callback."""
            logger.warning('Failed to register application: ' + str(error))
            mainloop.quit()
