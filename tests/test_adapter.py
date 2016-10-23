import subprocess
import sys
import unittest

import dbus
import dbusmock

from bluezero.adapter import Adapter


class TestBluezeroAdapter(dbusmock.DBusTestCase):

    @classmethod
    def setUpClass(klass):
        klass.start_system_bus()
        klass.dbus_con = klass.get_dbus(True)

        (klass.p_mock, klass.obj_bluez) = klass.spawn_server_template(
            'bluez5', {}, stdout=subprocess.PIPE)

    def setUp(self):
        # bluetoothd
        self.obj_bluez.Reset()
        self.dbusmock = dbus.Interface(self.obj_bluez, dbusmock.MOCK_IFACE)
        self.dbusmock_bluez = dbus.Interface(self.obj_bluez, 'org.bluez.Mock')
        self.adapter_device = 'hci0'
        self.adapter_name = 'Linux SBC'

    def test_adapter_address(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)
        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        self.assertEqual(dongle.address, '00:01:02:03:04:05')

    def test_adapter_name(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)
        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        self.assertEqual(dongle.name, self.adapter_name)

    def test_adapter_alias(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)
        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        self.assertEqual(dongle.alias, self.adapter_name)

    def test_adapter_alias_write(self):
        dev_name = 'my-test-dev'
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        dongle.alias = dev_name
        self.assertEqual(dongle.alias, dev_name)

    def test_class(self):
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        self.assertEqual(dongle.bt_class, 268)

    def test_adapter_power(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        self.assertEqual(dongle.powered, 1)

    def test_adapter_power_write(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        dongle.powered = 0
        self.assertEqual(dongle.powered, 0)

    def test_adapter_discoverable(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        self.assertEqual(dongle.discoverable, 1)

    def test_adapter_discoverable_write(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        dongle.discoverable = 0
        self.assertEqual(dongle.discoverable, 0)

    def test_adapter_pairable(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        self.assertEqual(dongle.pairable, 1)

    def test_adapter_pairable_write(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        dongle.pairable = 0
        self.assertEqual(dongle.pairable, 0)

    def test_adapter_pairabletimeout(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        self.assertEqual(dongle.pairabletimeout, 180)

    def test_adapter_pairabletimeout_write(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        dongle.pairabletimeout = 220
        self.assertEqual(dongle.pairabletimeout, 220)

    def test_adapter_discoverabletimeout(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        self.assertEqual(dongle.discoverabletimeout, 180)

    def test_adapter_discoverabletimeout_write(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        dongle.discoverabletimeout = 220
        self.assertEqual(dongle.discoverabletimeout, 220)

    def test_adapter_discovering(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        self.assertEqual(dongle.discovering, 1)

    @unittest.skip('mock of discovery not implemented')
    def test_start_discovery(self):
        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(self.adapter_device,
                                              self.adapter_name)

        self.assertEqual(path, '/org/bluez/' + self.adapter_device)
        dongle = Adapter(path)
        # test
        dongle.nearby_discovery()
        self.assertEqual(dongle.discovering, 1)


if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
