"""Classes required to create a Bluetooth Peripheral.

Current classes include:
- Service -- Bluetooth Service
- Characteristic -- Bluetooth Characteristic
- Descriptor -- Bluetooth Descriptor
"""
from __future__ import absolute_import, print_function, unicode_literals

# D-Bus imports
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# python-bluezero imports
from bluezero import constants

# Initialise the mainloop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


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

    :Example:

    >>> from bluezero import GATT
    >>> from bluezero import localGATT
    >>> from bluezero import tools
    >>> app = localGATT.Application()
    >>> srv = localGATT.Service(1, '180F', True)
    >>> app.add_managed_object(srv)
    >>> srv_mng = GATT.GattManager('/org/bluez/hci0')
    >>> srv_mng.register_application(app.get_path(), {})
    >>> tools.start_mainloop()

    """
    def __init__(self, device_id=None):
        """Default initialiser.

        1. Initialises the program loop using ``GObject``.
        2. Registers the Application on the D-Bus.
        3. Initialises the list of services offered by the application.

        """
        # Initialise the D-Bus path and register it
        self.bus = dbus.SystemBus()
        self.path = '/ukBaz/bluezero'
        self.bus_name = dbus.service.BusName('ukBaz.bluezero', self.bus)
        dbus.service.Object.__init__(self, self.bus_name, self.path)

        # Objects to be associated with this service
        self.managed_objs = []

    @dbus.service.method(constants.DBUS_OM_IFACE,
                         out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        """Get all objects that are managed by the application.

        Return type is a dictionary whose keys are each registered object and
        values the properties of the given object.
        """
        response = {}

        for object in self.managed_objs:
            for iface in object.props.keys():
                response[object.get_path()] = {iface: object.GetAll(iface)}

        return response

    def add_managed_object(self, object):
        """Add a service to the list of services offered by the Application.

        :param object: Python object of dbus path to be managed
        """
        self.managed_objs.append(object)

    def get_path(self):
        """Return the DBus object path"""
        return dbus.ObjectPath(self.path)


class Service(dbus.service.Object):
    """Bluez Service Class.

    This class represents a BLE Service.

    :Example:

    >>> your_service = localGATT.Service(service_id, UUID, primary)

    """

    PATH_BASE = '/ukBaz/bluezero/service'

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
    def GetAll(self, interface_name):
        """Return the service properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface: interface to get the properties of.

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
    def Get(self, interface_name, property_name):
        """DBus API for getting a property value"""

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
    def Set(self, interface_name, property_name, value, *args, **kwargs):
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
    def PropertiesChanged(self, interface, changed, invalidated):
        """Emit a Properties Changed notification signal.

        This signal is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``.
        """
        logger.debug('Service properties changed: ',
                     interface, changed, invalidated)


class Characteristic(dbus.service.Object):
    """Bluez Characteristic Class.

    This class represents a BLE Characteristic.

    :Example:

    >>> your_characteristic = localGATT.Characteristic(characteristic_id,
    >>>                                                UUID,
    >>>                                                service_obj,
    >>>                                                value,
    >>>                                                notifying,
    >>>                                                flags)
    """
    def __init__(self, characteristic_id,
                 uuid,
                 service_obj,
                 value,
                 notifying,
                 flags):
        """Default initialiser.

        1. Registers the characteristc on the D-Bus.
        2. Sets up the service UUID and primary flags.

        :param service_id:
        :param uuid: service BLE UUID
        :param service_obj: the service that this characteristic is part of
        :param value: the initial value of this characteristic
        :param notifying: boolean representing the state of notification
        :param flags:
        """
        # Setup D-Bus object paths and register service
        PATH_BASE = service_obj.get_path() + '/char'
        self.path = PATH_BASE + str('{0:04d}'.format(characteristic_id))
        self.bus = dbus.SystemBus()
        dbus.service.Object.__init__(self, self.bus, self.path)
        self.props = {
            constants.GATT_CHRC_IFACE: {
                'UUID': uuid,
                'Service': service_obj.get_path(),
                'Value': value,
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

    def add_call_back(self, callback):
        self.PropertiesChanged = callback

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface_name):
        """Return the service properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface: interface to get the properties of.

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
    def Get(self, interface_name, property_name):
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
    def Set(self, interface_name, property_name, value, *args, **kwargs):
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
    def PropertiesChanged(self, interface, changed, invalidated):
        """Emit a Properties Changed notification signal.

        This signal is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``.
        """
        logger.debug('Char Prop Changed')

    @dbus.service.method(constants.GATT_CHRC_IFACE,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        """
        DBus method for getting the characteristic value
        :return: value
        """
        return self.GetAll(constants.GATT_CHRC_IFACE)['Value']

    @dbus.service.method(constants.GATT_CHRC_IFACE,
                         in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        """
        DBus method for setting the characteristic value
        :return: value
        """
        self.Set(constants.GATT_CHRC_IFACE, 'Value', value)

    @dbus.service.method(constants.GATT_CHRC_IFACE,
                         in_signature='', out_signature='')
    def StartNotify(self):
        """
        DBus method for enabling notifications of the characteristic value.
        :return: value
        """
        if not self.props[constants.GATT_CHRC_IFACE]['Notifying'] is True:
            logger.info('Notifying already, nothing to do')
            return

        self.Set(constants.GATT_CHRC_IFACE,
                 'Notifying',
                 dbus.Boolean(True, variant_level=1))

    @dbus.service.method(constants.GATT_CHRC_IFACE,
                         in_signature='', out_signature='')
    def StopNotify(self):
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


class Descriptor(dbus.service.Object):
    """Bluez Descriptor Class.

    This class represents a BLE Descriptor.

    :Example:

    >>> your_descriptor = localGATT.Descriptor(descriptor_id,
    >>>                                        UUID,
    >>>                                        your_char,
    >>>                                        value,
    >>>                                        flags)
    """
    def __init__(self,
                 descriptor_id,
                 uuid,
                 characteristic_obj,
                 value,
                 flags):
        """Default initialiser.

        1. Registers the descriptor on the D-Bus.
        2. Sets up the service UUID and primary flags.

        :param descriptor_id: A unique identifier for this descriptor
        :param uuid: descriptor BLE UUID
        :param characteristic_obj: The characteristic that this descriptor
                                   is related to
        :param value: The initial value of the descriptor
        :param flags: Flags specifying access permissions
        """
        # Setup D-Bus object paths and register service
        PATH_BASE = characteristic_obj.get_path() + '/desc'
        self.path = PATH_BASE + str('{0:04d}'.format(descriptor_id))
        self.bus = dbus.SystemBus()
        dbus.service.Object.__init__(self, self.bus, self.path)
        self.props = {
            constants.GATT_DESC_IFACE: {
                'UUID': uuid,
                'Characteristic': characteristic_obj.get_path(),
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
    def GetAll(self, interface_name):
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
    def Get(self, interface_name, property_name):
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
    def Set(self, interface_name, property_name, value, *args, **kwargs):
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
    def PropertiesChanged(self, interface, changed, invalidated):
        """Emit a Properties Changed notification signal.

        This signal is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``.
        """
        return 0

    @dbus.service.method(constants.GATT_DESC_IFACE,
                         in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        """
        DBus method for getting the characteristic value
        :return: value
        """
        return self.GetAll(constants.GATT_DESC_IFACE)['Value']

    @dbus.service.method(constants.GATT_DESC_IFACE,
                         in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        """
        DBus method for setting the descriptor value
        :return:
        """
        return self.Set(constants.GATT_DESC_IFACE, 'Value', value)
