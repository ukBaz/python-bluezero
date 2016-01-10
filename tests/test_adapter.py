import sys
import subprocess
import unittest
import dbus
import dbus.mainloop.glib
import dbusmock
from gi.repository import GLib
from bluezero.adapter import Adapter


class TestBluezero(dbusmock.DBusTestCase):

    @classmethod
    def setUpClass(klass):
        klass.start_session_bus()
        klass.start_system_bus()
        klass.dbus_con = klass.get_dbus(True)

    def setUp(self):
        # bluetoothd
        (self.p_mock, self.obj_bluez) = self.spawn_server_template(
            'bluez5', {}, stdout=subprocess.PIPE)
        self.dbusmock_bluez = dbus.Interface(self.obj_bluez, 'org.bluez.Mock')
        # Set up an adapter and device.
        adapter_name = 'hci0'
        device_address = '11:22:33:44:55:66'
        device_alias = 'My Phone'

        ml = GLib.MainLoop()

        self.dbusmock_bluez.AddAdapter(adapter_name, 'my-computer')

    def tearDown(self):
        self.p_mock.terminate()
        self.p_mock.wait()

    def test_adapter_address(self):
        dongle = Adapter()
        self.assertEqual(dongle.address(), '00:01:02:03:04:05')

    def test_adapter_name(self):
        dongle = Adapter()
        self.assertEqual(dongle.name(), 'my-computer')

    def test_adapter_alias(self):
        dongle = Adapter()
        self.assertEqual(dongle.alias(), 'my-computer')

if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
