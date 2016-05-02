import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

from bluezero import bluezutils
from bluezero import adapter

import array
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject


"""
##  GATT Server
"""
BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE = 'org.bluez.GattDescriptor1'


class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'


class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'


class Application(dbus.service.Object):
    def __init__(self):
        GObject.threads_init()
        dbus.mainloop.glib.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = GObject.MainLoop()
        self.bus = dbus.SystemBus()
        self.path = '/ukBaz/bluezero/application'
        self.services = []
        dbus.service.Object.__init__(self, self.bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    def get_primary_service(self):
        # services = self.GetManagedObjects()
        primary_uuid = None
        for service in self.services:
            if service.primary:
                print(service.uuid)
                primary_uuid = service.uuid
        return primary_uuid

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
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

    def start(self):

        dongle = adapter.Adapter()
        dongle.powered('on')

        print('setup ad_manager')
        ad_manager = bluezutils.get_advert_manager_interface()

        print('setup service_manager')
        service_manager = bluezutils.get_gatt_manager_interface()

        print('Advertise service')
        service_ad = Advertisement(self, 'peripheral')
        primary_uuid = self.get_primary_service()
        service_ad.add_service_uuid(primary_uuid)

        print('Register Adver', service_ad.get_path())
        ad_manager.RegisterAdvertisement(service_ad.get_path(), {},
                                         reply_handler=register_ad_cb,
                                         error_handler=register_ad_error_cb)

        # print('Register Application', app.get_path())
        print('Register Application ', self.get_path())
        service_manager.RegisterApplication(
            self.get_path(), {},
            reply_handler=register_service_cb,
            error_handler=register_service_error_cb)
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            print('Closing Mainloop')
            self.mainloop.quit()


class Service(dbus.service.Object):

    PATH_BASE = '/ukBaz/bluezero/service1'

    def __init__(self, uuid, primary):
        self.index = id(self)
        self.path = self.PATH_BASE + str(self.index)
        self.bus = dbus.SystemBus()
        dbus.service.Object.__init__(self, self.bus, self.path)
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array(
                    self.get_characteristic_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
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


def find_ad_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if LE_ADVERTISING_MANAGER_IFACE in props:
            return o

    return None


def find_gatt_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props:
            return o

    return None


def register_service_cb():
    print('GATT application registered')


def register_service_error_cb(error):
    print('Failed to register application: ' + str(error))
    # mainloop.quit()


class Characteristic(dbus.service.Object):
    def __init__(self, uuid, flags, service, value=None):
        self.index = id(self)
        self.path = service.path + '/char' + str(self.index)
        self.bus = service.bus
        self.index = service.index
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.notifying = False
        self.descriptors = []
        self.value = value
        self.notify_cb = None
        self.write_cb = None
        dbus.service.Object.__init__(self, self.bus, self.path)

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                'Service': self.service.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
                'Descriptors': dbus.Array(
                    self.get_descriptor_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()

    @dbus.service.method(GATT_CHRC_IFACE, out_signature='ay')
    def ReadValue(self):
        # print('Reading Characteristic', self.value)
        if self.value is None:
            self.value = 0
        return [dbus.Byte(self.value)]

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='ay')
    def WriteValue(self, value):
        # print('Writing Characteristic', value)
        # if not self.writable:
        #     raise NotPermittedException()
        self.value = value
        if self.write_cb is not None:
            # print('Write callback')
            self.write_cb()

    def add_write_event(self, object_id):
        self.write_cb = object_id

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_cb()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self.notify_cb()

    def notify_cb(self):
        print('Default StartNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

    def add_notify_event(self, object_id):
        self.notify_cb = object_id

    def send_notify_event(self, value):
        # print('send', self, value)
        self.value = value
        if not self.notifying:
            print('Not notifying')
            return
        # print('Update prop')
        self.PropertiesChanged(
            GATT_CHRC_IFACE,
            {'Value': [dbus.Byte(self.value)]}, [])


class Descriptor(dbus.service.Object):
    def __init__(self, uuid, flags, characteristic):
        self.index = id(self)
        self.path = characteristic.path + '/desc' + str(self.index)
        self.bus = characteristic.bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, self.bus, self.path)

    def get_properties(self):
        return {
            GATT_DESC_IFACE: {
                'Characteristic': self.chrc.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()

    @dbus.service.method(GATT_DESC_IFACE, out_signature='ay')
    def ReadValue(self):
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='ay')
    def WriteValue(self, value):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()


class UserDescriptor(Descriptor):
    """
    Writable CUD descriptor.

    """
    CUD_UUID = '2901'

    def __init__(self, name, characteristic):
        self.writable = 'writable-auxiliaries' in characteristic.flags
        #self.value = array.array('B', bytes(name, encoding='utf-8'))
        self.value = array.array('B', bytes(name))
        self.value = self.value.tolist()
        Descriptor.__init__(
            self,
            self.CUD_UUID,
            ['read', 'write'],
            characteristic)

    def ReadValue(self):
        # print('Read Value: ', self.value)
        return self.value

    def WriteValue(self, value):
        # print('Write Value: ', value)
        if not self.writable:
            raise NotPermittedException()
        self.value = value

"""
##  Start of Advertisement
"""
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'


class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'


class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'


class Advertisement(dbus.service.Object):
    PATH_BASE = '/ukBaz/bluezero/advertisement'

    def __init__(self, service, advertising_type):
        # print('**Service', service)
        self.index = id(self)
        self.path = self.PATH_BASE + str(self.index)
        self.ad_type = advertising_type
        # print('Service uuid', service.uuid)
        # print('Advert path', self.path)
        # print('Service bus', service.bus)
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.include_tx_power = None
        dbus.service.Object.__init__(self, service.bus, self.path)

    def get_properties(self):
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
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_solicit_uuid(self, uuid):
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = dict()
        self.manufacturer_data[manuf_code] = data

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dict()
        self.service_data[uuid] = data

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        # print('GetAll')
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        # print('returning props')
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        print('%s: Released!' % self.path)


def register_ad_cb():
    print('Advertisement registered')


def register_ad_error_cb(error):
    print('Failed to register advertisement: ' + str(error))
    # mainloop.quit()

"""
##  End of Advertisement
"""
