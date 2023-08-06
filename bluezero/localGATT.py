"""Classes required to create a Bluetooth Peripheral."""

from inspect import signature

# D-Bus imports
import dbus
import dbus.exceptions
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

# python-bluezero imports
from bluezero import async_tools
from bluezero import constants
from bluezero import dbus_tools
from bluezero import tools

DBusGMainLoop(set_as_default=True)

logger = tools.create_module_logger(__name__)


########################################
# Exception classes
#######################################
class InvalidArgsException(dbus.exceptions.DBusException):
    """This is a D-Bus exception class for Invalid Arguments.

    All this class does is set the internal variable ``_dbus_error_name`` to
    the object path for D-Bus Invalid Argument Exceptions.

    """

    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class Application(dbus.service.Object):
    """Bluez Application Class.

    This is the parent class for a python Bluez application.

    """
    def __init__(self):
        """Default initialiser.

        """
        # Initialise the D-Bus path and register it
        self.bus = dbus.SystemBus()
        self.path = dbus.ObjectPath(constants.BLUEZERO_DBUS_OBJECT)
        dbus.service.Object.__init__(self, self.bus, self.path)

        # Objects to be associated with this service
        self.managed_objs = []
        self.eventloop = async_tools.EventLoop()

    @dbus.service.method(constants.DBUS_OM_IFACE,
                         out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):  # pylint: disable=invalid-name
        """Get all objects that are managed by the application.

        Return type is a dictionary whose keys are each registered object and
        values the properties of the given object.
        """
        response = {}

        for obj in self.managed_objs:
            for iface in obj.props.keys():
                response[obj.get_path()] = {iface: obj.GetAll(iface)}

        return response

    def add_managed_object(self, service_obj):
        """Add a service to the list of services offered by the Application.

        :param service_obj: Python object of dbus path to be managed
        """
        self.managed_objs.append(service_obj)

    def get_path(self):
        """Return the DBus object path"""
        return dbus.ObjectPath(self.path)

    def start(self):
        """Start event loop"""
        self.eventloop.run()

    def stop(self):
        """Stop event loop"""
        self.eventloop.quit()


class Service(dbus.service.Object):
    """Bluez Service Class.

    This class represents a BLE Service.

    :Example:

    >>> your_service = localGATT.Service(service_id, UUID, primary)

    """

    PATH_BASE = f'{constants.BLUEZERO_DBUS_OBJECT}/service'

    def __init__(self, service_id, uuid, primary):
        """Default initialiser.

        1. Registers the service on the D-Bus.
        2. Sets up the service UUID and primary flags.

        :param service_id:
        :param uuid: service BLE UUID
        :param primary: whether or not the service is a primary service
        """
        # Setup D-Bus object paths and register service
        self.path = self.PATH_BASE + str('{0:04d}'.format(service_id))
        self.bus = dbus.SystemBus()
        self.interface = constants.GATT_SERVICE_IFACE
        dbus.service.Object.__init__(self, self.bus, self.path)
        self.props = {
            constants.GATT_SERVICE_IFACE: {
                'UUID': uuid,
                'Primary': primary}
        }

    def get_path(self):
        """Return the DBus object path"""
        return dbus.ObjectPath(self.path)

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface_name):  # pylint: disable=invalid-name
        """Return the service properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface_name: interface to get the properties of.

        The interface must be ``org.bluez.GattService1`` otherwise an
        exception is raised.
        """
        if interface_name != constants.GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        try:
            return self.props[interface_name]
        except KeyError:
            raise dbus.exceptions.DBusException(
                'no such interface ' + interface_name,
                name=interface_name + '.UnknownInterface')

    @dbus.service.method(dbus.PROPERTIES_IFACE,
                         in_signature='ss', out_signature='v')
    def Get(self,  # pylint: disable=invalid-name
            interface_name, property_name):
        """
        DBus API for getting a property value

        :param interface_name:
        :param property_name:
        :return:
        """

        if interface_name != constants.GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        try:
            return self.GetAll(interface_name)[property_name]
        except KeyError:
            raise dbus.exceptions.DBusException(
                'no such property ' + property_name,
                name=interface_name + '.UnknownProperty')

    @dbus.service.method(dbus.PROPERTIES_IFACE,
                         in_signature='ssv', out_signature='')
    def Set(self, interface_name,  # pylint: disable=invalid-name
            property_name, value):
        """Standard D-Bus API for setting a property value"""

        try:
            iface_props = self.props[interface_name]
        except KeyError:
            raise dbus.exceptions.DBusException(
                'no such interface ' + interface_name,
                name=self.interface + '.UnknownInterface')

        if property_name not in iface_props:
            raise dbus.exceptions.DBusException(
                'no such property ' + property_name,
                name=self.interface + '.UnknownProperty')

        iface_props[property_name] = value

        self.PropertiesChanged(interface_name,
                               dbus.Dictionary({property_name: value},
                                               signature='sv'),
                               dbus.Array([], signature='s'))

    @dbus.service.signal(constants.DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self,  # pylint: disable=invalid-name
                          interface, changed, invalidated):
        """Emit a Properties Changed notification signal.

        This signal is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``.
        """
        logger.debug('Service properties changed: %s, %s, %s',
                     interface, changed, invalidated)


class Characteristic(dbus.service.Object):
    """
    Bluez Characteristic Class.

    This class represents a BLE Characteristic.
    """
    def __init__(self,
                 service_id,
                 characteristic_id,
                 uuid,
                 value,
                 notifying,
                 flags,
                 read_callback=None,
                 write_callback=None,
                 notify_callback=None):
        self.read_callback = read_callback
        self.write_callback = write_callback
        self.notify_callback = notify_callback

        # Setup D-Bus object paths and register service
        service_path = (f'{constants.BLUEZERO_DBUS_OBJECT}/'
                        f'service{service_id:04d}')
        self.path = f'{service_path}/char{characteristic_id:04d}'
        self.bus = dbus.SystemBus()
        dbus.service.Object.__init__(self, self.bus, self.path)
        self.props = {
            constants.GATT_CHRC_IFACE: {
                'UUID': uuid,
                'Service': dbus_tools.get_dbus_obj(service_path),
                'Value': dbus.Array(value, signature='y'),
                'Notifying': notifying,
                'Flags': flags}
        }

        for prop in self.props[constants.GATT_CHRC_IFACE].keys():
            self.Set(constants.GATT_CHRC_IFACE,
                     prop,
                     self.props[constants.GATT_CHRC_IFACE][prop])

    def get_path(self):
        """Return the DBus object path"""
        return dbus.ObjectPath(self.path)

    @property
    def is_notifying(self):
        """Get the current notify status"""
        return bool(self.Get(constants.GATT_CHRC_IFACE, 'Notifying'))

    def set_value(self, value):
        """
        Set the value of the characteristic. Will create notify event
        if notifications are enabled

        :param value: list of integers in little endian format
        """
        self.Set(constants.GATT_CHRC_IFACE, 'Value',
                 dbus.Array(value, signature='y'))

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface_name):  # pylint: disable=invalid-name
        """Return the service properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface_name: interface to get the properties of.

        The interface must be ``org.bluez.GattCharacteristic1`` otherwise an
        exception is raised.
        """
        if interface_name != constants.GATT_CHRC_IFACE:
            raise InvalidArgsException()

        try:
            return self.props[interface_name]
        except KeyError:
            raise dbus.exceptions.DBusException(
                'no such interface ' + interface_name,
                name=interface_name + '.UnknownInterface')

    @dbus.service.method(dbus.PROPERTIES_IFACE,
                         in_signature='ss', out_signature='v')
    def Get(self,  # pylint: disable=invalid-name
            interface_name, property_name):
        """DBus API for getting a property value.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface_name: interface to get the properties of.
        :param property_name: request this property
        """

        if interface_name != constants.GATT_CHRC_IFACE:
            raise InvalidArgsException()

        try:
            return self.GetAll(interface_name)[property_name]
        except KeyError:
            raise dbus.exceptions.DBusException(
                'no such property ' + property_name,
                name=interface_name + '.UnknownProperty')

    @dbus.service.method(dbus.PROPERTIES_IFACE,
                         in_signature='ssv', out_signature='')
    def Set(self, interface_name,   # pylint: disable=invalid-name
            property_name, value):
        """Standard D-Bus API for setting a property value"""

        if property_name not in self.props[constants.GATT_CHRC_IFACE]:
            raise dbus.exceptions.DBusException(
                'no such property ' + property_name,
                name=constants.GATT_CHRC_IFACE + '.UnknownProperty')
        self.props[constants.GATT_CHRC_IFACE][property_name] = value
        return self.PropertiesChanged(interface_name,
                                      dbus.Dictionary({property_name: value},
                                                      signature='sv'),
                                      dbus.Array([], signature='s'))

    @dbus.service.signal(constants.DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self,  # pylint: disable=invalid-name
                          interface, changed, invalidated):
        """Emit a Properties Changed notification signal.

        This signal is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``.
        """
        logger.debug('Char Prop Changed')

    @dbus.service.method(constants.GATT_CHRC_IFACE,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):  # pylint: disable=invalid-name
        """
        DBus method for getting the characteristic value

        :return: value
        """
        if self.read_callback:
            if len(signature(self.read_callback).parameters) == 1:
                value = self.read_callback(dbus_tools.dbus_to_python(options))
            else:
                value = self.read_callback()
            self.Set(constants.GATT_CHRC_IFACE, 'Value',
                     dbus.Array(value, signature='y'))
            logger.debug('ReadValue: %s', value)
        return self.GetAll(constants.GATT_CHRC_IFACE)['Value']

    @dbus.service.method(constants.GATT_CHRC_IFACE,
                         in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):  # pylint: disable=invalid-name
        """
        DBus method for setting the characteristic value

        :return: value
        """
        if self.write_callback:
            self.write_callback(dbus_tools.dbus_to_python(value),
                                dbus_tools.dbus_to_python(options))
        self.Set(constants.GATT_CHRC_IFACE, 'Value', value)

    @dbus.service.method(constants.GATT_CHRC_IFACE,
                         in_signature='', out_signature='')
    def StartNotify(self):  # pylint: disable=invalid-name
        """
        DBus method for enabling notifications of the characteristic value.

        :return: value
        """
        if self.props[constants.GATT_CHRC_IFACE]['Notifying'] is True:
            logger.info('Notifying already, nothing to do')
            return
        self.Set(constants.GATT_CHRC_IFACE,
                 'Notifying',
                 dbus.Boolean(True, variant_level=1))
        if self.notify_callback:
            self.notify_callback(True, self)

    @dbus.service.method(constants.GATT_CHRC_IFACE,
                         in_signature='', out_signature='')
    def StopNotify(self):  # pylint: disable=invalid-name
        """
        DBus method for disabling notifications of the characteristic value.

        :return: value
        """
        if self.props[constants.GATT_CHRC_IFACE]['Notifying'] is False:
            logger.info('Not Notifying, nothing to do')
            return

        self.Set(constants.GATT_CHRC_IFACE,
                 'Notifying',
                 dbus.Boolean(False, variant_level=1))
        if self.notify_callback:
            self.notify_callback(False, self)


class Descriptor(dbus.service.Object):
    """
    Bluez Descriptor Class.

    This class represents a BLE Descriptor.
    """
    def __init__(self,
                 service_id,
                 characteristic_id,
                 descriptor_id,
                 uuid,
                 value,
                 flags):
        # Setup D-Bus object paths and register service
        char_path = (f'{constants.BLUEZERO_DBUS_OBJECT}/'
                     f'service{service_id:04d}/char{characteristic_id:04d}')
        self.path = f'{char_path}/desc{descriptor_id:04d}'
        self.bus = dbus.SystemBus()
        dbus.service.Object.__init__(self, self.bus, self.path)
        self.props = {
            constants.GATT_DESC_IFACE: {
                'UUID': uuid,
                'Characteristic': dbus_tools.get_dbus_obj(char_path),
                'Value': value,
                'Flags': flags}
        }
        for prop in self.props[constants.GATT_DESC_IFACE].keys():
            self.Set(constants.GATT_DESC_IFACE,
                     prop,
                     self.props[constants.GATT_DESC_IFACE][prop])

    def get_path(self):
        """Return the DBus object path"""
        return dbus.ObjectPath(self.path)

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface_name):  # pylint: disable=invalid-name
        """Return the descriptor properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface: interface to get the properties of.

        The interface must be ``org.bluez.GattDescriptor1`` otherwise an
        exception is raised.
        """
        if interface_name != constants.GATT_DESC_IFACE:
            raise InvalidArgsException()

        try:
            return self.props[interface_name]
        except KeyError:
            raise dbus.exceptions.DBusException(
                'no such interface ' + interface_name,
                name=interface_name + '.UnknownInterface')

    @dbus.service.method(dbus.PROPERTIES_IFACE,
                         in_signature='ss', out_signature='v')
    def Get(self,   # pylint: disable=invalid-name
            interface_name, property_name):
        """DBus API for getting a property value.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface_name: interface to get the properties of.
        :param property_name: request this property
        """

        if interface_name != constants.GATT_DESC_IFACE:
            raise InvalidArgsException()

        try:
            return self.GetAll(interface_name)[property_name]
        except KeyError:
            raise dbus.exceptions.DBusException(
                'no such property ' + property_name,
                name=interface_name + '.UnknownProperty')

    @dbus.service.method(dbus.PROPERTIES_IFACE,
                         in_signature='ssv', out_signature='')
    def Set(self, interface_name,  # pylint: disable=invalid-name
            property_name, value):
        """Standard D-Bus API for setting a property value"""

        if property_name not in self.props[constants.GATT_DESC_IFACE]:
            raise dbus.exceptions.DBusException(
                'no such property ' + property_name,
                name=constants.GATT_DESC_IFACE + '.UnknownProperty')

        self.props[interface_name][property_name] = value

        return self.PropertiesChanged(interface_name,
                                      dbus.Dictionary({property_name: value},
                                                      signature='sv'),
                                      dbus.Array([], signature='s'))

    @dbus.service.signal(constants.DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self,  # pylint: disable=invalid-name
                          interface, changed, invalidated):
        """Emit a Properties Changed notification signal.

        This signal is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``.
        """
        return 0

    @dbus.service.method(constants.GATT_DESC_IFACE,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):  # pylint: disable=invalid-name
        """
        DBus method for getting the characteristic value

        :return: value
        """
        return self.GetAll(constants.GATT_DESC_IFACE)['Value']

    @dbus.service.method(constants.GATT_DESC_IFACE,
                         in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):  # pylint: disable=invalid-name
        """
        DBus method for setting the descriptor value

        :return:
        """
        return self.Set(constants.GATT_DESC_IFACE, 'Value', value)
