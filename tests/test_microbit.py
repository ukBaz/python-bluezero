import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants


def mock_get(iface, prop):
    if iface == 'org.bluez.Device1':
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_1C'][iface][prop]
    elif iface == 'org.bluez.Adapter1':
        return tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop]
    elif iface == 'org.bluez.Characteristic1':
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_B1/service0031/char0035'][iface][prop]


def mock_read(options):
    print('test')


def mock_set(iface, prop, value):
    tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop] = value


class TestBluezeroMicrobit(unittest.TestCase):

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
        self.dbus_mock.Interface.return_value.ReadValue = mock_read
        self.dbus_mock.SystemBus = MagicMock()
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import microbit
        self.module_under_test = microbit

    def tearDown(self):
        self.module_patcher.stop()

    def test_load(self):
        ubit = self.module_under_test.Microbit(adapter_addr='00:00:00:00:5A:AD',
                                               device_addr='E4:43:33:7E:54:1C')

    def test_connected(self):
        ubit = self.module_under_test.Microbit(adapter_addr='00:00:00:00:5A:AD',
                                               device_addr='E4:43:33:7E:54:1C')
        self.assertEqual(ubit.connected, True)

    @unittest.skip('Need to mock GATT ReadValue')
    def test_scroll_delay(self):
        ubit = self.module_under_test.Microbit(adapter_addr='00:00:00:00:5A:AD',
                                               device_addr='E4:43:33:7E:54:1C')
        self.assertEqual(ubit.display_scroll_delay(), 23)
