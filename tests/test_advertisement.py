import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants

adapter_props = tests.obj_data.full_ubits


def mock_get(iface, prop):
    return tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop]


def mock_set(iface, prop, value):
    tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop] = value


def mock_register_advertisement(advert_obj, options):
    for prop in advert_obj.props[constants.LE_ADVERTISEMENT_IFACE]:
        tests.obj_data['/org/bluez/hci0']['org.bluez.LEAdvertisingManager1'][prop] = advert_obj[constants.LE_ADVERTISEMENT_IFACE][prop]


class TestBluezeroAdvertisement(unittest.TestCase):

    def setUp(self):
        """
        Patch the DBus module
        :return:
        """
        self.dbus_mock = MagicMock()
        self.dbus_exception_mock = MagicMock()
        self.dbus_service_mock = MagicMock()
        self.mainloop_mock = MagicMock()
        self.gobject_mock = MagicMock()

        modules = {
            'dbus': self.dbus_mock,
            'dbus.exceptions': self.dbus_exception_mock,
            'dbus.service': self.dbus_service_mock,
            'dbus.mainloop.glib': self.mainloop_mock,
            'gi.repository': self.gobject_mock,
        }
        self.dbus_mock.Interface.return_value.GetManagedObjects.return_value = tests.obj_data.full_ubits
        self.dbus_mock.Interface.return_value.Get = mock_get
        self.dbus_mock.Interface.return_value.Set = mock_set
        self.dbus_mock.return_value
        self.dbus_mock.SystemBus = MagicMock()
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import advertisement
        from bluezero import dbus_tools
        self.module_under_test = advertisement
        self.module_tools = dbus_tools

    def tearDown(self):
        self.module_patcher.stop()

    def test_beacon_default_adapter(self):
        beacon = self.module_under_test.Advertisement(1, 'broadcast')
        beacon.service_UUIDs = ['FEAA']
        beacon.service_data = {'FEAA': [0x10, 0x00, 0x00, 0x63, 0x73,
                                        0x72, 0x00, 0x61, 0x62, 0x6f,
                                        0x75, 0x74]}
        ad_manager = self.module_under_test.AdvertisingManager('00:00:00:00:5A:AD')
        ad_manager.register_advertisement(beacon, {})
        result = self.module_tools.get_managed_objects()['/org/bluez/hci0']['org.bluez.LEAdvertisingManager1']
        self.assertDictEqual({}, result)
