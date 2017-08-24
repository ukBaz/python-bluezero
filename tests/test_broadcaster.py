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


class TestBluezeroBroadcaster(unittest.TestCase):
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
        self.dbus_mock.SystemBus = MagicMock()
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import broadcaster
        from bluezero import adapter
        self.bz_adapter = adapter
        self.module_under_test = broadcaster
        self.path = '/org/bluez/hci0/dev_D4_AE_95_4C_3E_A4'
        self.adapter_path = '/org/bluez/hci0'
        self.dev_name = 'BBC micro:bit [zezet]'
        self.address = 'D4:AE:95:4C:3E:A4'

    def tearDown(self):
        self.module_patcher.stop()

    def test_beacon_default_adapter(self):
        my_beacon = self.module_under_test.Beacon()
    #
    # def test_beacon_specified_adapter(self):
    #     beacon2 = self.module_under_test.Beacon('00:00:00:00:5A:AD')

    # def test_service_data(self):
    #     my_beacon = self.module_under_test.Beacon()
    #     my_beacon.add_service_data('FEAA': [0x10, 0x00, 0x00, 0x63, 0x73,
    #                                            0x72, 0x00, 0x61, 0x62, 0x6f,
    #                                            0x75, 0x74])
    #     self.assertEqual(my_beacon.serivce)
