"""Classes that represent the GATT features of a remote device."""

import dbus

from bluezero import constants
from bluezero import dbus_tools
from bluezero import device
from bluezero import tools


logger = tools.create_module_logger(__name__)


class Service:
    """Remote GATT Service."""

    def __init__(self, adapter_addr, device_addr, srv_uuid):
        """
        Remote GATT Service Initialisation.

        :param adapter_addr: Adapter address.
        :param device_addr: device address.
        :param srv_uuid: Service UUID.
        """
        self.adapter_addr = adapter_addr
        self.device_addr = device_addr
        self.srv_uuid = srv_uuid
        self.rmt_device = device.Device(adapter_addr, device_addr)
        self.service_methods = None
        self.service_props = None

        if self.rmt_device.services_resolved:
            self.resolve_gatt()

    def resolve_gatt(self):
        """
        Get the methods and properties for the discovered Services

        :return:
        """
        if self.rmt_device.services_resolved:
            self.service_methods = dbus_tools.get_methods(self.adapter_addr,
                                                          self.device_addr,
                                                          self.srv_uuid)
            self.service_props = dbus_tools.get_props(self.adapter_addr,
                                                      self.device_addr,
                                                      self.srv_uuid)

    @property
    def UUID(self):  # pylint: disable=invalid-name
        """
        Return the value of the Service UUID for this path.

        :return: string for example '00001800-0000-1000-8000-00805f9b34fb'
        """
        return self.service_props.Get(
            constants.GATT_SERVICE_IFACE, 'UUID')

    @property
    def device(self):
        """
        Return the DBus object that this service belongs to.

        :return: DBus object of device
        """
        return self.service_props.Get(
            constants.GATT_SERVICE_IFACE, 'Device')

    @property
    def primary(self):
        """
        Return a boolean saying if this a primary service.

        :return: boolean
        """
        return self.service_props.Get(
            constants.GATT_SERVICE_IFACE, 'Primary')


class Characteristic:
    """Remote GATT Characteristic."""

    def __init__(self, adapter_addr, device_addr, srv_uuid, chrc_uuid):
        """
        Remote GATT Characteristic Initialisation.

        :param adapter_addr: Adapter address.
        :param device_addr: device address.
        :param srv_uuid: Service UUID.
        :param chrc_uuid: Characteristic UUID.
        """
        self.adapter_addr = adapter_addr
        self.device_addr = device_addr
        self.rmt_device = device.Device(adapter_addr, device_addr)
        self.srv_uuid = srv_uuid
        self.chrc_uuid = chrc_uuid
        self.characteristic_methods = None
        self.characteristic_props = None
        self._prop_chngd_sig = None

    def resolve_gatt(self):
        """
        Get the methods and properties for the discovered characteristics

        :return: Boolean of if characteristics have been resolved
        """
        logger.info('Resolving GATT database for %s', self.chrc_uuid)
        if self.rmt_device.services_resolved:
            self.characteristic_methods = dbus_tools.get_methods(
                self.adapter_addr,
                self.device_addr,
                self.srv_uuid,
                self.chrc_uuid)
            self.characteristic_props = dbus_tools.get_props(
                self.adapter_addr,
                self.device_addr,
                self.srv_uuid,
                self.chrc_uuid)
            return True
        return False

    @property
    def UUID(self):  # pylint: disable=invalid-name
        """
        Return the value of the Characteristic UUID for this path.

        :return: string example '00002a00-0000-1000-8000-00805f9b34fb'
        """
        return self.characteristic_props.Get(
            constants.GATT_CHRC_IFACE, 'UUID')

    @property
    def service(self):
        """
        Return the DBus object for this characteristic's service.

        :return: DBus object of device
        """
        return self.characteristic_props.Get(
            constants.GATT_CHRC_IFACE, 'Service')

    @property
    def value(self):
        """
        The cached value of the characteristic.

        This property gets updated only after a successful read request and
        when a notification or indication is received, upon which a
        PropertiesChanged signal will be emitted.

        :return: DBus byte array
        """
        return self.read_raw_value()

    @value.setter
    def value(self, new_value):
        if not isinstance(new_value, list):
            new_value = [new_value]
        self.write_value(new_value)

    @property
    def notifying(self):
        """
        Return whether this characteristic has notifications enabled.

        :return: Boolean
        """
        return self.characteristic_props.Get(
            constants.GATT_CHRC_IFACE, 'Notifying')

    @property
    def flags(self):
        """
        Return a list of how this characteristic's value can be used.

        :return: list example ['read', 'write', 'notify']
        """
        return self.characteristic_props.Get(
            constants.GATT_CHRC_IFACE, 'Flags')

    def read_raw_value(self, flags=''):
        """
        Return this characteristic's value (if allowed).

        :param flags: "offset": Start offset
                      "device": Device path (Server only)
        :return:

        Possible Errors:    org.bluez.Error.Failed
                            org.bluez.Error.InProgress
                            org.bluez.Error.NotPermitted
                            org.bluez.Error.InvalidValueLength
                            org.bluez.Error.NotAuthorized
                            org.bluez.Error.NotSupported
        """
        try:
            return self.characteristic_methods.ReadValue(dbus.Array())
        except AttributeError:
            logger.error('Service: %s with Characteristic: %s not defined on '
                         'device: %s', self.srv_uuid, self.chrc_uuid,
                         self.device_addr)
            return []

    def write_value(self, value, flags=''):
        """
        Write a new value to the characteristic.

        :param value: A list of byte values
        :param flags: Optional dictionary.
            Typically empty. Values defined at:
            https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/gatt-api.txt
        """
        try:
            self.characteristic_methods.WriteValue(value, dbus.Array(flags))
        except AttributeError:
            logger.error('Service: %s with Characteristic: %s not defined '
                         'on device: %s. Cannot write_value',  self.srv_uuid,
                         self.chrc_uuid, self.device_addr)

    def start_notify(self):
        """Initialise notifications for this characteristic."""
        try:
            self.characteristic_methods.StartNotify(
                reply_handler=self.start_notify_cb,
                error_handler=generic_error_cb,
                dbus_interface=constants.GATT_CHRC_IFACE)
        except AttributeError:
            logger.error('Service: %s with Characteristic: %s not defined '
                         'on device: %s. Cannot start_notify',  self.srv_uuid,
                         self.chrc_uuid, self.device_addr)

    def stop_notify(self):
        """Stop notifications for this characteristic."""
        try:
            self.characteristic_methods.StopNotify(
                reply_handler=self.stop_notify_cb,
                error_handler=generic_error_cb,
                dbus_interface=constants.GATT_CHRC_IFACE)
        except AttributeError:
            logger.error('Service: %s with Characteristic: %s not defined on'
                         'on device: %s', self.srv_uuid, self.chrc_uuid,
                         self.device_addr)

    def add_characteristic_cb(self, callback=None):
        """
        Add a callback for this characteristic.

        :param callback: callback function to be added.
        """
        if callback is None:
            self._prop_chngd_sig.remove()
        else:
            self._prop_chngd_sig = self.characteristic_props.connect_to_signal(
                'PropertiesChanged', callback)

    def props_changed_cb(self, iface, changed_props, invalidated_props):
        """
        Callback indicating that properties have changed.

        :param iface: Interface associated with the callback.
        :param changed_props: Properties changed that triggered the callback.
        :param invalidated_props: Unused.
        """
        if iface != constants.GATT_CHRC_IFACE:
            return

        if not changed_props:
            return

        value = changed_props.get('Value', None)
        if not value:
            return

        logger.debug('Properties changed: ', value)

    def start_notify_cb(self):
        """Callback associated with enabling notifications."""
        logger.info('Notifications enabled')

    def stop_notify_cb(self):
        """Callback associated with disabling notifications."""
        logger.info('Notifications disabled')


class Descriptor:
    """Remote GATT Descriptor."""

    def __init__(self, adapter_addr, device_addr,
                 srv_uuid, chrc_uuid, dscr_uuid):
        """
        Remote GATT Descriptor Initialisation.

        :param adapter_addr: Adapter address.
        :param device_addr: device address.
        :param srv_uuid: Service UUID.
        :param chrc_uuid: Characteristic UUID.
        :param dscr_uuid: Descriptor UUID.
        """
        self.adapter_addr = adapter_addr
        self.device_addr = device_addr
        self.rmt_device = device.Device(adapter_addr, device_addr)
        self.srv_uuid = srv_uuid
        self.chrc_uuid = chrc_uuid
        self.dscr_uuid = dscr_uuid
        self.descriptor_methods = None
        self.descriptor_props = None

        if self.rmt_device.services_resolved:
            self.resolve_gatt()

    @property
    def UUID(self):  # pylint: disable=invalid-name
        """
        Return the value of the Descriptor UUID for this path.

        :return: string example '00002a00-0000-1000-8000-00805f9b34fb'
        """
        return self.descriptor_props.Get(constants.GATT_DESC_IFACE, 'UUID')

    @property
    def characteristic(self):
        """
        Object path of the GATT characteristic's descriptor.

        :return: DBus object
        """
        return self.descriptor_props.Get(constants.GATT_DESC_IFACE, 'UUID')

    @property
    def value(self):
        """
        The cached value of the descriptor.

        This property gets updated only after a successful read request, upon
        which a PropertiesChanged signal will be emitted.

        :return: DBus byte array
        """
        return self.descriptor_props.Get(
            constants.GATT_CHRC_IFACE, 'Value')

    @property
    def flags(self):
        """
        Return a list of how this descriptor value can be used.

        :return: list example ['read', 'write']
        """
        return self.descriptor_props.Get(
            constants.GATT_CHRC_IFACE, 'Flags')

    def read_raw_value(self, flags=''):
        """
        Issue a request to read the value of the descriptor.

        Returns the value if the operation was successful.

        :param flags: "offset": Start offset
                      "device": Device path (Server only)

        :return: dbus byte array
        """
        return self.descriptor_methods.ReadValue(dbus.Array(flags))

    def write_value(self, value, flags=''):
        """
        Issue a request to write the value of the descriptor.

        :param value: DBus byte array
        :param flags: "offset": Start offset
                      "device": Device path (Server only)

        :return:
        """
        self.descriptor_methods.WriteValue(value, dbus.Array(flags))


class Profile:
    """Remote GATT Profile."""

    def __init__(self, adapter_addr, device_addr, profile_uuid):
        """
        Remote GATT Profile Initialisation.

        :param profile_path: dbus path to the profile.
        """
        self.profile_path = dbus_tools.get_profile_path(adapter_addr,
                                                        device_addr,
                                                        profile_uuid)
        self.bus = dbus.SystemBus()
        self.profile_object = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.profile_path)
        self.profile_methods = dbus.Interface(
            self.profile_object,
            constants.GATT_PROFILE_IFACE)
        self.profile_props = dbus.Interface(self.profile_object,
                                            dbus.PROPERTIES_IFACE)

    def release(self):
        """
        Release the profile.

        :return:
        """
        self.profile_methods.Release()

    @property
    def UUIDs(self):  # pylint: disable=invalid-name
        """
        128-bit GATT service UUIDs to auto connect.

        :return: list of UUIDs
        """
        return self.profile_props.Get(constants.GATT_PROFILE_IFACE, 'UUIDs')


def generic_error_cb(error):
    """Generic Error Callback function."""
    logger.error('D-Bus call failed: %s', str(error))


def register_app_cb():
    """Application registration callback."""
    logger.info('GATT application registered')


def register_app_error_cb(error):
    """Application registration error callback."""
    logger.warning('Failed to register application: %s', str(error))
    # mainloop.quit()


class GattManager:
    """GATT Manager."""

    def __init__(self, adapter_addr):
        """
        GATT Manager Initialisation.

        :param manager_path: dbus path to the GATT Manager.
        """
        self.manager_path = dbus_tools.get_dbus_path(adapter_addr)
        self.bus = dbus.SystemBus()
        self.manager_obj = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.manager_path)
        self.manager_methods = dbus.Interface(
            self.manager_obj,
            constants.GATT_MANAGER_IFACE)
        self.manager_props = dbus.Interface(self.manager_obj,
                                            dbus.PROPERTIES_IFACE)

    def register_application(self, application, options):
        """
        Register an application with the GATT Manager.

        :param application: Application object.
        :param options:
        :return:
        """
        self.manager_methods.RegisterApplication(
            application.get_path(),
            dbus.Dictionary(options, signature='sv'),
            reply_handler=register_app_cb,
            error_handler=register_app_error_cb
        )

    def unregister_application(self, application):
        """
        Unregister an application with the GATT Manager.

        :param application: Application object.
        :return:
        """
        self.manager_methods.UnregisterApplication(application)
