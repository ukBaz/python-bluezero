import subprocess
import sys
import unittest

import dbus
import dbus.mainloop.glib
import dbusmock
from gi.repository import GLib

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

    def tearDown(self):
        self.p_mock.terminate()
        self.p_mock.wait()

    def test_adapter_address(self):
        # Chosen parameters.
        adapter_name = 'hci0'
        system_name = 'my-computer'

        # Add an adapter
        path = self.dbusmock_bluez.AddAdapter(adapter_name, system_name)
        self.assertEqual(path, '/org/bluez/' + adapter_name)
        dongle = Adapter(path)
        self.assertEqual(dongle.address(), '00:01:02:03:04:05')

    def test_adapter_name(self):
        dongle = Adapter('/org/bluez/hci0')
        self.assertEqual(dongle.name(), 'my-computer')

    def test_adapter_alias(self):
        dongle = Adapter('/org/bluez/hci0')
        self.assertEqual(dongle.alias(), 'my-computer')

    def test_adapter_alias_write(self):
        dev_name = 'my-test-dev'
        dongle = Adapter('/org/bluez/hci0')
        dongle.alias(dev_name)
        self.assertEqual(dongle.alias(), dev_name)

    def test_adapter_power(self):
        dongle = Adapter('/org/bluez/hci0')
        self.assertEqual(dongle.powered(), 1)

    def test_adapter_power_write(self):
        dongle = Adapter('/org/bluez/hci0')
        dongle.powered(0)
        self.assertEqual(dongle.powered(), 0)

    def test_adapter_discoverable(self):
        dongle = Adapter('/org/bluez/hci0')
        self.assertEqual(dongle.discoverable(), 1)

    def test_adapter_discoverabletimeout(self):
        dongle = Adapter('/org/bluez/hci0')
        self.assertEqual(dongle.discoverabletimeout(), 180)

    def test_adapter_pairable(self):
        dongle = Adapter('/org/bluez/hci0')
        self.assertEqual(dongle.pairable(), 1)

    def test_adapter_pairabletimeout(self):
        dongle = Adapter('/org/bluez/hci0')
        self.assertEqual(dongle.pairabletimeout(), 180)

    def test_adapter_discovering(self):
        dongle = Adapter('/org/bluez/hci0')
        self.assertEqual(dongle.discovering(), 0)

    def test_start_discovery(self):
        dongle = Adapter('/org/bluez/hci0')
        dongle.nearby_discovery()
        self.assertEqual(dongle.discovering(), 1)

if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
