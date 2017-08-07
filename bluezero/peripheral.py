"""Classes required to create a Bluetooth Peripheral.

Current classes include:

- Application -- Root class
- Service -- Bluetooth Service
- Characteristic -- Bluetooth Characteristic
- Descriptor -- Bluetooth Descriptor
- Advertisement -- Bluetooth Advertisement
"""

# D-Bus imports
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

# python-bluezero imports
from bluezero import tools
from bluezero import adapter
from bluezero import constants

# array import
import array

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# Main eventloop import
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject


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


class NotSupportedException(dbus.exceptions.DBusException):
    """This is a D-Bus exception class for Unsupported Bluez Exceptions.

    All this class does is set the internal variable ``_dbus_error_name`` to
    the object path for Bluez Unsupported Exceptions.

    """

    _dbus_error_name = 'org.bluez.Error.NotSupported'


class NotPermittedException(dbus.exceptions.DBusException):
    """This is a D-Bus exception class for Not Permitted Bluez Exceptions.

    All this class does is set the internal variable ``_dbus_error_name`` to
    the object path for Bluez Not Permitted Exceptions.

    """

    _dbus_error_name = 'org.bluez.Error.NotPermitted'


class InvalidValueLengthException(dbus.exceptions.DBusException):
    """This is a D-Bus exception class for Bluez Invalid Value Length Exceptions.

    All this class does is set the internal variable ``_dbus_error_name`` to
    the object path for Bluez Invalid Value Length Exceptions.

    """

    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'


class FailedException(dbus.exceptions.DBusException):
    """This is a D-Bus exception class for Bluez Failed Exceptions.

    All this class does is set the internal variable ``_dbus_error_name`` to
    the object path for Bluez Failed Exceptions.

    """

    _dbus_error_name = 'org.bluez.Error.Failed'

###################
# Application Class
###################


class Application(dbus.service.Object):
    """Bluez Application Class.

    This is the parent class for a python Bluez application.

    :Example:

    >>> app = peripheral.Application()
    >>> app.add_service(Service)
    >>> app.start()
    """

    def __init__(self, device_id=None):
        """Default initialiser.

        1. Initialises the program loop using ``GObject``.
        2. Registers the Application on the D-Bus.
        3. Initialises the list of services offered by the application.

        """
        # Initialise the loop that the application runs in
        GObject.threads_init()
        dbus.mainloop.glib.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = GObject.MainLoop()

        # Initialise the D-Bus path and register it
        self.bus = dbus.SystemBus()
        self.path = '/ukBaz/bluezero/application{}'.format(id(self))
        self.bus_name = dbus.service.BusName('ukBaz.bluezero', self.bus)
        dbus.service.Object.__init__(self, self.bus_name, self.path)

        # Initialise services within the application
        self.services = []

        self.dongle = adapter.Adapter(device_id)

    def get_path(self):
        """Return the D-Bus object path."""
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        """Add a service to the list of services offered by the Application.

        :param service: the service to be added (type: peripheral.Service)
        """
        self.services.append(service)

    def get_primary_service(self):
        """Get the *primary* service registered with the Application."""
        # services = self.GetManagedObjects()
        primary_uuid = None
        for service in self.services:
            if service.primary:
                logger.debug(service.uuid)
                primary_uuid = service.uuid
        return primary_uuid

    @dbus.service.method(constants.DBUS_OM_IFACE,
                         out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        """Get all objects that are managed by the application.

        Return type is a dictionary whose keys are each registered object and
        values the properties of the given object.
        """
        response = {}
        print('GetManagedObjects')

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response

    def add_device_name(self, device_name):
        """
        Set the Bluetooth friendly name for the device

        :param device_name: a string to be used as the name
        """
        self.dongle.alias = device_name

    def start(self):
        """Start the application.

        This function performs the following steps to start the BLE peripheral
        application:

        1. Registers the Bluetooth adapter and turns it on.
        2. Gets the Bluez D-Bus advertising manager interface.
        3. Gets the Bluez D-Bus gatt manager interface.
        4. Creates an advertisement with the primary application service.
        5. Registers the advertisement with the Bluez advertising manager.
        6. Registers the application with the Bluez gatt manager.
        7. Runs the program loop

        The application must first have had a service added to it.

        :Example:

        >>> app = peripheral.Application()
        >>> app.add_service(your_service)
        >>> app.start()

        It is good practice to put the ``app.start()`` in a
        ``try-except-finally`` block to enable keyboard interrupts.
        """
        # Register the Bluetooth adapter
        self.dongle.powered = True

        # Setup the advertising manager
        print('setup ad_manager')
        self.ad_manager = tools.get_advert_manager_interface()

        # Setup the service manager
        print('setup service_manager')
        self.service_manager = tools.get_gatt_manager_interface()

        # Setup the advertisement
        self.service_ad = Advertisement(self, 'peripheral')
        for service in self.services:
            if service.primary:
                print('Advertising service ', service.uuid)
                self.service_ad.add_service_uuid(service.uuid)
                self.service_ad.ad_type = service.type
                if service.service_data is not None:
                    print('Adding service data: ',
                          service.uuid,
                          service.service_data)
                    self.service_ad.add_service_data(service.uuid,
                                                     service.service_data)

        # Register the advertisement
        print('Register Adver', self.service_ad.get_path())
        self.ad_manager.RegisterAdvertisement(
            self.service_ad.get_path(), {},
            reply_handler=register_ad_cb,
            error_handler=register_ad_error_cb)

        # Register the application
        print('Register Application ', self.get_path())
        self.service_manager.RegisterApplication(
            self.get_path(), {},
            reply_handler=register_service_cb,
            error_handler=register_service_error_cb)
        try:
            # Run the mainloop
            self.mainloop.run()
        except KeyboardInterrupt:
            print('Closing Mainloop')
            self.mainloop.quit()

    def stop(self):
        """Stop the application.

        1. Unregister the advertisement from the Bluez advertising manager
        2. Unregister the application from the Bluez Gatt manager
        3. Stop the program loop.

        """
        # self.ad_manager.UnregisterAdvertisement(self.service_ad.get_path())
        self.service_manager.UnregisterApplication(self.get_path())
        self.mainloop.quit()

##########################################
# Service Class and Registration Callbacks
##########################################


class Service(dbus.service.Object):
    """Bluez Service Class.

    This class represents a BLE Service.

    :Example:

    >>> your_service = peripheral.Service(UUID, primary)

    """

    PATH_BASE = '/ukBaz/bluezero/service1'

    def __init__(self, uuid, primary, type='peripheral'):
        """Default initialiser.

        1. Registers the service on the D-Bus.
        2. Sets up the service UUID and primary flags.
        3. Initialises the list of characteristics associated with the service.

        :param uuid: service BLE UUID
        :param primary: whether or not the service is a primary service
        """
        # Setup D-Bus object paths and register service
        self.index = id(self)
        self.path = self.PATH_BASE + str(self.index)
        self.bus = dbus.SystemBus()
        dbus.service.Object.__init__(self, self.bus, self.path)

        # Setup UUID, primary flag
        self.uuid = uuid
        self.primary = primary
        self.type = type
        self.service_data = None

        # Initialise characteristics within the service
        self.characteristics = []

    def UUID(self):
        """Return Service UUID"""
        return self.service.Get(constants.GATT_SERVICE_IFACE, 'UUID')

    def get_properties(self):
        """Return a dictionary of the service properties.

        The dictionary has the following keys:

        - UUID: the service UUID
        - Primary: whether the service is the primary service
        - Characteristics: D-Bus array of the characteristic object paths
          associated with the service.

        """
        return {
            constants.GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array(
                    self.get_characteristic_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        """Return the D-Bus object path."""
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        """Add a characteristic.

        Adds a characteristic to the list of characteristics offered by the
        service.

        :param characteristic: the characteristic to be added.
                               (type: peripheral.Characteristic)

        """
        self.characteristics.append(characteristic)

    def add_service_data(self, service_data):
        """
        Add service data to be include with advertisement
        :param service_data: list of hex values to be used as service data
        """
        self.service_data = service_data

    def get_characteristic_paths(self):
        """Return the D-Bus object paths of all service characteristics."""
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        """Return a list of the service characteristics."""
        return self.characteristics

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        """Return the service properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface: interface to get the properties of.

        The interface must be ``org.bluez.GattService1`` otherwise an
        exception is raised.
        """
        if interface != constants.GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()

    @dbus.service.method(constants.DBUS_OM_IFACE,
                         out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        """Get all objects that are managed by the service.

        Return type is a dictionary whose keys are each registered object and
        values the properties of the given object.
        """
        response = {}
        # print('GetManagedObjects')

        response[self.get_path()] = self.get_properties()
        chrcs = self.get_characteristics()
        for chrc in chrcs:
            response[chrc.get_path()] = chrc.get_properties()
            descs = chrc.get_descriptors()
            for desc in descs:
                response[desc.get_path()] = desc.get_properties()

        return response


def register_service_cb():
    """Service registration callback."""
    print('GATT application registered')


def register_service_error_cb(error):
    """Service registration error callback."""
    print('Failed to register application: ' + str(error))
    # mainloop.quit()

######################
# Characteristic Class
######################


class Characteristic(dbus.service.Object):
    """Bluez Characteristic Class.

    This class represents a BLE Characteristic.
    """

    def __init__(self, uuid, flags, service, value=None):
        """"Default initialiser.

        1. Registers the characteristic on the service path.
        2. Sets up initial values.

        :param uuid: characteristic BLE UUID.
        :param flags: characteristic flags.
        :param service: service that the characteristic is associated with.
        :param value: (optional) characteristic value.
        """
        # Register the characteristic on the service path
        self.index = id(self)
        self.path = service.path + '/char' + str(self.index)
        self.bus = service.bus
        dbus.service.Object.__init__(self, self.bus, self.path)

        self.index = service.index
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.notifying = False
        self.descriptors = []
        self.value = value
        self.notify_cb = None
        self.write_cb = None

    def get_properties(self):
        """Return a dictionary of the characteristic properties.

        The dictionary has the following keys:

        - Service: the characteristic's service
        - UUID: the characteristic UUID
        - Flags: any characteristic flags
        - Descriptors: D-Bus array of the descriptor object paths
          associated with the characteristic.

        """
        return {
            constants.GATT_CHRC_IFACE: {
                'Service': self.service.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
                'Descriptors': dbus.Array(
                    self.get_descriptor_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        """Return the D-Bus object path."""
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        """Add a descriptor.

        Adds a descriptor to the list of descriptors offered by the
        characteristic.

        :param descriptor: the descriptor to be added.
                               (type: peripheral.Descriptor)

        """
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        """Return the D-Bus object paths of all characteristic descriptors."""
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        """Return a list of the characteristic descriptors."""
        return self.descriptors

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        """Return the characteristic properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface: interface to get the properties of.

        The interface must be ``org.bluez.GattCharacteristic1`` otherwise an
        exception is raised.
        """
        if interface != constants.GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()

    @dbus.service.method(constants.GATT_CHRC_IFACE,
                         in_signature='a{sv}',
                         out_signature='ay')
    def ReadValue(self, options):
        """Return the characteristic value.

        This method is registered with the D-Bus at
        ``org.bluez.GattCharacteristic1``.
        """
        # print('Reading Characteristic', self.value)
        if self.value is None:
            self.value = 0
        return [dbus.Byte(self.value)]

    @dbus.service.method(constants.GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        """Set the characteristic value.

        This method is registered with the D-Bus at
        ``org.bluez.GattCharacteristic1``.

        The characteristic value is set, and if any additional write callback
        is registered this is executed.

        :param value: the value that the characteristic is set to.
        """
        # print('Writing Characteristic', value)
        # if not self.writable:
        #     raise NotPermittedException()
        self.value = int.from_bytes(value, byteorder='little', signed=False)
        if self.write_cb is not None:
            # print('Write callback')
            self.write_cb()

    def add_write_event(self, object_id):
        """Add a write callback.

        The write callback is executed when WriteValue(val) is executed.

        :param object_id: The object ID of the write callback.
        """
        self.write_cb = object_id

    @dbus.service.method(constants.GATT_CHRC_IFACE)
    def StartNotify(self):
        """Start BLE notifications for the characteristic.

        This method is registered with the D-Bus at
        ``org.bluez.GattCharacteristic1``.
        """
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_cb()

    @dbus.service.method(constants.GATT_CHRC_IFACE)
    def StopNotify(self):
        """Stop BLE notifications for the characteristic.

        This method is registered with the D-Bus at
        ``org.bluez.GattCharacteristic1``.
        """
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self.notify_cb()

    def notify_cb(self):
        """Notification callback."""
        print('Default StartNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.signal(constants.DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        """Emit a Properties Changed notification signal.

        This signal is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``.
        """
        pass

    def add_notify_event(self, object_id):
        """Add a notification callback.

        The notification callback is executed when StartNotify() is executed.

        :param object_id: The object ID of the notification callback.
        """
        self.notify_cb = object_id

    def send_notify_event(self, value):
        """Send a notification event.

        :param value: the value that the characteristic is to be set to.

        This function sets the characteristic value, and if the characteristic
        is set to notify emits a PropertiesChanged() signal with the new value.
        """
        # print('send', self, value)
        self.value = value
        if not self.notifying:
            print('Not notifying')
            return
        # print('Update prop')
        self.PropertiesChanged(
            constants.GATT_CHRC_IFACE,
            {'Value': [dbus.Byte(self.value)]}, [])

####################
# Descriptor Classes
####################


class Descriptor(dbus.service.Object):
    """Bluez Descriptor Class.

    This class represents a BLE Descriptor, and should always be inherited
    (see UserDescriptor).

    .. seealso:: :class:`UserDescriptor`
    """

    def __init__(self, uuid, flags, characteristic):
        """"Default initialiser.

        1. Registers the descriptor on the characteristic path.
        2. Sets up initial values.

        :param uuid: descriptor BLE UUID.
        :param flags: descriptor flags.
        :param characteristic: characteristic that the descriptor is associated
                               with.
        """
        # Register the descriptor on the characteristic path
        self.index = id(self)
        self.path = characteristic.path + '/desc' + str(self.index)
        self.bus = characteristic.bus
        dbus.service.Object.__init__(self, self.bus, self.path)

        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic

    def get_properties(self):
        """Return a dictionary of the descriptor properties.

        The dictionary has the following keys:

        - Characteristic: the descriptor's characteristic
        - UUID: the descriptor UUID
        - Flags: any descriptor flags

        """
        return {
            constants.GATT_DESC_IFACE: {
                'Characteristic': self.chrc.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
            }
        }

    def get_path(self):
        """Return the D-Bus object path."""
        return dbus.ObjectPath(self.path)

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        """Return the descriptor properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface: interface to get the properties of.

        The interface must be ``org.bluez.GattDescriptor1`` otherwise an
        exception is raised.
        """
        if interface != constants.GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()

    @dbus.service.method(constants.GATT_DESC_IFACE,
                         in_signature='a{sv}',
                         out_signature='ay')
    def ReadValue(self, options):
        """Return the descriptor value.

        This method is registered with the D-Bus at
        ``org.bluez.GattDescriptor1``.

        This function is implemented in child classes.
        """
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(constants.GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        """Set the descriptor value.

        This method is registered with the D-Bus at
        ``org.bluez.GattCharacteristic1``.

        This function is implemented in child classes.
        """
        print('Default WriteValue called, returning error')
        raise NotSupportedException()


class UserDescriptor(Descriptor):
    """Sample Bluez Descriptor Class.

    This class represents a writeable BLE Descriptor.

    .. seealso:: :class:`Descriptor`
    """

    CUD_UUID = '2901'

    def __init__(self, name, characteristic):
        """"Default initialiser.

        1. Sets the descriptor as writeable.
        2. Sets the descriptor name.
        3. Calls the parent initialisation to finish.

        :param name: descriptor name.
        :param characteristic: characteristic that the descriptor is associated
                               with.
        """
        self.writable = 'writable-auxiliaries' in characteristic.flags
        # self.value = array.array('B', bytes(name, encoding='utf-8'))
        self.value = array.array('B', str.encode(name, 'utf-8'))
        self.value = self.value.tolist()
        Descriptor.__init__(
            self,
            self.CUD_UUID,
            ['read', 'write'],
            characteristic)

    def ReadValue(self, options):
        """Return the descriptor value.

        *(NB: This method is registered with the D-Bus at
        ``org.bluez.GattDescriptor1``.)*
        """
        # print('Read Value: ', self.value)
        return self.value

    def WriteValue(self, value, options):
        """Set the descriptor value.

        *(NB: This method is registered with the D-Bus at
        ``org.bluez.GattCharacteristic1``.)*

        Checks that the descriptor is writeable, and if so writes the value.
        """
        # print('Write Value: ', value)
        if not self.writable:
            raise NotPermittedException()
        self.value = value

###################################
# Advertisement Class and Callbacks
###################################


class Advertisement(dbus.service.Object):
    """Bluez Advertisement Class.

    This class is used to create and manage everything required for the BLE
    service to be advertised.

    .. seealso:: :class:`Application`
    """

    PATH_BASE = '/ukBaz/bluezero/advertisement'

    def __init__(self, service, advertising_type):
        """"Default initialiser.

        1. Registers the advertisement on the service path.
        2. Sets up initial values.

        :param service: service that the advertisement is associated with.
        :param advertising_type: type of advertisement
        """
        # print('**Service', service)
        self.index = id(self)
        self.path = self.PATH_BASE + str(self.index)
        dbus.service.Object.__init__(self, service.bus, self.path)

        self.ad_type = advertising_type
        # print('Service uuid', service.uuid)
        # print('Advert path', self.path)
        # print('Service bus', service.bus)
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.include_tx_power = None

    def get_properties(self):
        """Return a dictionary of the advert properties.

        The dictionary has the following keys:

        - Type: the advertisement type.
        - ServiceUUIDS: UUIDs of services to advertise
        - SolicitUUIDS:
        - ManufacturerData: dictionary of manufacturer data
        - ServiceData: dictionary of service data
        - IncludeTxPower:

        """
        properties = dict()
        properties['Type'] = self.ad_type
        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,
                                                    signature='s')
        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,
                                                    signature='s')
        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(
                self.manufacturer_data, signature='qay')
        if self.service_data is not None:
            properties['ServiceData'] = dbus.Dictionary(self.service_data,
                                                        signature='say')
        if self.include_tx_power is not None:
            properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
        return {constants.LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        """Return the D-Bus object path."""
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        """Add service UUIDs to the advertisement.

        :param uuid: UUID of the service to add.
        """
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_solicit_uuid(self, uuid):
        """Add solicit UUIDs to the advertisement.

        :param uuid: UUID of the service to add.
        """
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def add_manufacturer_data(self, manuf_code, data):
        """Add manufacturer data to the advertisement.

        :param manuf_code: manufacturing code.
        :param data: corresponding data for the given manuf_code.

        The data is stored as a dictionary with keys ``manuf_code`` and values
        ``data``.
        """
        if not self.manufacturer_data:
            self.manufacturer_data = dict()
        self.manufacturer_data[manuf_code] = data

    def add_service_data(self, uuid, data):
        """Add manufacturer data to the advertisement.

        :param uuid: service uuid.
        :param data: corresponding data for the given service uuid.

        The data is stored as a dictionary with keys ``uuid`` and values
        ``data``.
        """
        if not self.service_data:
            self.service_data = dict()
        self.service_data[uuid] = data

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        """Return the advert properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface: interface to get the properties of.

        The interface must be ``org.bluez.LEAdvertisement1`` otherwise an
        exception is raised.
        """
        # print('GetAll')
        if interface != constants.LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        # print('returning props')
        return self.get_properties()[constants.LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(constants.LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        """Release an advert.

        This method is registered with the D-Bus at
        ``org.bluez.LEAdvertisement1``.
        """
        print('%s: Released!' % self.path)


def register_ad_cb():
    """Advertisement registration callback."""
    print('Advertisement registered')


def register_ad_error_cb(error):
    """Advertisement registration error callback."""
    print('Failed to register advertisement: ' + str(error))
    # mainloop.quit()
