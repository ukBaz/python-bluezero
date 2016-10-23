import subprocess
import sys
import unittest

import dbus
import dbusmock

from bluezero.adapter import Adapter
from bluezero.device import Device


class TestBluezeroDevice(dbusmock.DBusTestCase):

    @classmethod
    def setUpClass(klass):
        klass.start_system_bus()
        klass.dbus_con = klass.get_dbus(True)
        (klass.p_mock, klass.obj_bluez) = klass.spawn_server_template(
            'bluez5', {}, stdout=subprocess.PIPE)

    def setUp(self):
        self.obj_bluez.Reset()
        self.dbusmock = dbus.Interface(self.obj_bluez, dbusmock.MOCK_IFACE)
        self.dbusmock_bluez = dbus.Interface(self.obj_bluez, 'org.bluez.Mock')

        self.adapter_name = 'hci0'
        self.address = '22:22:33:44:55:66'
        self.alias = 'Peripheral Device'

        self.adapter_path = self.dbusmock_bluez.AddAdapter(self.adapter_name,
                                                           'my-computer')
        self.assertEqual(self.adapter_path, '/org/bluez/' + self.adapter_name)
        dongle = Adapter('/org/bluez/hci0')

        self.device_path = self.dbusmock_bluez.AddDevice(self.adapter_name,
                                                         self.address,
                                                         self.alias)
        self.assertEqual(self.device_path,
                         '/org/bluez/' + self.adapter_name + '/dev_' +
                         self.address.replace(':', '_'))
        self.ble_dev = Device('/org/bluez/hci0/dev_22_22_33_44_55_66')

    def test_device_name(self):
        self.assertEqual(self.ble_dev.name, self.alias)

    def test_connected(self):
        conn_state = self.ble_dev.connected
        self.assertEqual(conn_state, False)
        self.dbusmock_bluez.ConnectDevice(self.adapter_name,
                                          self.address)
        conn_state = self.ble_dev.connected
        self.assertEqual(conn_state, True)

    def test_address(self):
        self.assertEqual(self.ble_dev.address, self.address)

    def test_name(self):
        self.assertEqual(self.ble_dev.name, self.alias)

    @unittest.skip('Do not know value to use for icon')
    def test_icon(self):
        pass

    @unittest.skip('Do not know value to use for class')
    def test_class(self):
        pass

    def test_appearance(self):
        self.assertEqual(self.ble_dev.appearance, 0x0200)

    def test_uuids(self):
        self.assertEqual(self.ble_dev.uuids,
                         ['00001800-0000-1000-8000-00805f9b34fb',
                          '00001801-0000-1000-8000-00805f9b34fb',
                          '0000180a-0000-1000-8000-00805f9b34fb'])

    def test_paired(self):
        self.assertEqual(self.ble_dev.paired, False)

    def test_trusted(self):
        self.assertEqual(self.ble_dev.trusted, False)

    def test_blocked(self):
        self.assertEqual(self.ble_dev.blocked, False)

    def test_alias(self):
        self.assertEqual(self.ble_dev.alias, self.alias)

    def test_adapter(self):
        self.assertEqual(self.ble_dev.adapter, self.adapter_path)

    def test_legacy_pairing(self):
        self.assertEqual(self.ble_dev.legacy_pairing, False)

    @unittest.skip('Do not know value to use for modalias')
    def test_modalias(self):
        pass

    def test_rssi(self):
        self.assertEqual(self.ble_dev.RSSI, -79)

    def test_txpower(self):
        self.assertEqual(self.ble_dev.tx_power, 0)

    @unittest.skip('Do not know value to use for manufacturer data')
    def test_manufacturer_data(self):
        pass

    @unittest.skip('Do not know value to use for service data')
    def test_service_data(self):
        pass

    def test_services_resolved(self):
        self.assertEqual(self.ble_dev.services_resolved, False)

    @unittest.skip('Not in BlueZ 5.42')
    def test_adverting_flags(self):
        pass


if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
