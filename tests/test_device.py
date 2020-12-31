import sys
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants


def mock_get(iface, prop):
    return tests.obj_data.full_ubits['/org/bluez/hci0/dev_D4_AE_95_4C_3E_A4'][iface][prop]


def mock_set(iface, prop, value):
    tests.obj_data.full_ubits['/org/bluez/hci0/dev_D4_AE_95_4C_3E_A4'][iface][prop] = value


class TestBluezeroDevice(unittest.TestCase):

    def setUp(self):
        """
        Patch the DBus module
        :return:
        """
        self.dbus_mock = MagicMock()
        self.mainloop_mock = MagicMock()
        self.gobject_mock = MagicMock()

        modules = {
            'dbus': self.dbus_mock,
            'dbus.exceptions': self.dbus_mock,
            'dbus.mainloop.glib': self.mainloop_mock,
            'gi.repository': self.gobject_mock,
        }
        self.dbus_mock.Interface.return_value.GetManagedObjects.return_value = tests.obj_data.full_ubits
        self.dbus_mock.Interface.return_value.Get = mock_get
        self.dbus_mock.Interface.return_value.Set = mock_set
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import device
        self.module_under_test = device
        self.path = '/org/bluez/hci0/dev_D4_AE_95_4C_3E_A4'
        self.adapter_path = '/org/bluez/hci0'
        self.dev_name = 'BBC micro:bit [zezet]'
        self.adapter_addr = '00:00:00:00:5A:AD'
        self.device_addr = 'D4:AE:95:4C:3E:A4'

    def tearDown(self):
        self.module_patcher.stop()

    def test_bad_device(self):
        self.assertRaises(ValueError,
                          self.module_under_test.Device,
                          self.adapter_addr,
                          "bad_device_address")

    def test_device_name(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.name, self.dev_name)

    def test_connected(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        conn_state = ble_dev.connected
        self.assertEqual(conn_state, False)
        """
        self.dbusmock_bluez.ConnectDevice(self.adapter_name,
                                          self.address)
        conn_state = self.ble_dev.connected
        self.assertEqual(conn_state, True)
    """
    def test_address(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.address, self.device_addr)

    def test_name(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.name, self.dev_name)

    @unittest.skip('Do not know value to use for icon')
    def test_icon(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.icon, 'dave')

    @unittest.skip('Do not know value to use for class')
    def test_class(self):
        pass

    def test_appearance(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.appearance, 0x0200)

    def test_uuids(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.uuids,
                         ['00001800-0000-1000-8000-00805f9b34fb',
                          '00001801-0000-1000-8000-00805f9b34fb',
                          '0000180a-0000-1000-8000-00805f9b34fb',
                          'e95d0753-251d-470a-a062-fa1922dfa9a8',
                          'e95d127b-251d-470a-a062-fa1922dfa9a8',
                          'e95d6100-251d-470a-a062-fa1922dfa9a8',
                          'e95d9882-251d-470a-a062-fa1922dfa9a8',
                          'e95dd91d-251d-470a-a062-fa1922dfa9a8',
                          'e95df2d8-251d-470a-a062-fa1922dfa9a8'])

    def test_paired(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.paired, False)

    def test_trusted(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.trusted, False)

    def test_blocked(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.blocked, False)

    def test_alias(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.alias, self.dev_name)

    def test_adapter(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev._adapter, self.adapter_path)

    def test_legacy_pairing(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.legacy_pairing, False)

    @unittest.skip('Do not know value to use for modalias')
    def test_modalias(self):
        pass

    @unittest.skip('No value from BlueZ for RSSI')
    def test_rssi(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.RSSI, -79)

    @unittest.skip('No value from BlueZ for Tx Power')
    def test_txpower(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.tx_power, 0)

    @unittest.skip('No test data for Manufacturer Data')
    def test_manufacturer_data(self):
        pass

    @unittest.skip('No test data for Service Data')
    def test_service_data(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)

    def test_services_resolved(self):
        ble_dev = self.module_under_test.Device(self.adapter_addr, self.device_addr)
        self.assertEqual(ble_dev.services_resolved, False)

    @unittest.skip('Not in BlueZ 5.42')
    def test_adverting_flags(self):
        pass

if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
