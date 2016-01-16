import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import argparse

import array
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

from random import randint

mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

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
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.include_tx_power = None
        dbus.service.Object.__init__(self, bus, self.path)

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
        print('GetAll')
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        print('returning props')
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        print('%s: Released!' % self.path)


class TestAdvertisement(Advertisement):

    def __init__(self, bus, index, url):
        Advertisement.__init__(self, bus, index, 'broadcast')
        self.add_service_uuid('FEAA')
        self.add_manufacturer_data(0xFEAA, [0x01, 0x06])
        """
        # Adafruit
        # self.add_service_data('FEAA',
        [0x10, 0x00, 0x00, 0x61, 0x64, 0x61, 0x66,
        0x72, 0x75, 0x69, 0x74, 0x07])
        # CamJam
        # self.add_service_data('FEAA',
        [0x10, 0x00, 0x02, 0x63, 0x61, 0x6D, 0x6A,
        0x61, 0x6D, 0x2E, 0x6D, 0x65, 0x2F])
        # BBC
        # self.add_service_data('FEAA',
        [0x10, 0x00, 0x00, 0x62, 0x62, 0x63, 0x2E,
        0x63, 0x6F, 0x2E, 0x75, 0x6B, 0x2F])
        """
        service_data = self.url_to_advert(url, 0x10, 0x00)
        self.add_service_data('FEAA', service_data)
        self.include_tx_power = False

    def url_to_advert(self, url, frame_type, tx_power):
        """
        Encode as specified
        https://github.com/google/eddystone/blob/master/eddystone-url/README.md
        :param url:
        :return:
        """
        prefix_sel = None
        prefix_start = None
        prefix_end = None
        suffix_sel = None
        suffix_start = None
        suffix_end = None

        prefix = ('http://www.', 'https://www.', 'http://', 'https://')

        suffix = ('.com/', '.org/', '.edu/', '.net/',
                  '.info/', '.biz/', '.gov/', '.com',
                  '.org', '.edu', '.net', '.info',
                  '.biz', '.gov'
                  )
        encode_search = True

        for x in prefix:
            if x in url and encode_search is True:
                # print('match prefix ' + url)
                prefix_sel = prefix.index(x)
                prefix_start = url.index(prefix[prefix_sel])
                prefix_end = len(prefix[prefix_sel]) + prefix_start
                encode_search = False

        encode_search = True
        for y in suffix:
            if y in url and encode_search is True:
                # print('match suffix ' + y)
                suffix_sel = suffix.index(y)
                suffix_start = url.index(suffix[suffix_sel])
                suffix_end = len(suffix[suffix_sel]) + suffix_start
                encode_search = False

        service_data = [frame_type]
        service_data.extend([tx_power])
        if suffix_start is None:
            suffix_start = len(url)
            service_data.extend([prefix_sel])
            for x in range(prefix_end, suffix_start):
                service_data.extend([ord(url[x])])
        elif suffix_end == len(url):
            service_data.extend([prefix_sel])
            for x in range(prefix_end, suffix_start):
                service_data.extend([ord(url[x])])
            service_data.extend([suffix_sel])
        else:
            service_data.extend([prefix_sel])
            for x in range(prefix_end, suffix_start):
                service_data.extend([ord(url[x])])
            service_data.extend([suffix_sel])
            for x in range(suffix_end, len(url)):
                service_data.extend([ord(url[x])])

        return service_data


def register_ad_cb():
    print('Advertisement registered')


def register_ad_error_cb(error):
    print('Failed to register advertisement: ' + str(error))
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.iteritems():
        if LE_ADVERTISING_MANAGER_IFACE in props:
            return o

    return None


def main(url):
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print('LEAdvertisingManager1 interface not found')
        return

    adapter_props = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                   "org.freedesktop.DBus.Properties")

    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)

    test_advertisement = TestAdvertisement(bus, 0, url)

    mainloop = GObject.MainLoop()

    ad_manager.RegisterAdvertisement(test_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    mainloop.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='The url to be advertised')
    args = parser.parse_args()
    main(args.url)
