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
        klass.start_session_bus()
        klass.start_system_bus()
        klass.dbus_con = klass.get_dbus(True)

    def setUp(self):
        # bluetoothd
        (self.p_mock, self.obj_bluez) = self.spawn_server_template(
            'tests/dbusmock_templates/bluezero.py', {}, stdout=subprocess.PIPE)
        self.dbusmock_bluez = dbus.Interface(self.obj_bluez, 'org.bluez.Mock')
        # Set up an adapter and device.
        adapter_name = 'hci0'
        device_address = '11:22:33:44:55:66'
        device_alias = 'My Phone'

        ml = GLib.MainLoop()

        self.dbusmock_bluez.AddAdapter(adapter_name, 'my-computer')
        self.dbusmock_bluez.AddDevice(
            adapter_name,
            device_address,
            device_alias)

    def tearDown(self):
        self.p_mock.terminate()
        self.p_mock.wait()

    def test_adapter_address(self):
        dongle = Adapter('/org/bluez/hci0')
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
        dongle.powered('on')
        self.assertEqual(dongle.powered(), 1)

    def test_adapter_power_write(self):
        dongle = Adapter('/org/bluez/hci0')
        dongle.powered('off')
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
