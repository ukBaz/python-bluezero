import subprocess
import sys
import unittest

import dbus
import dbus.mainloop.glib
import dbusmock
from gi.repository import GLib

from bluezero.adapter import Adapter
from bluezero.device import Device


class TestBluezeroDevice(dbusmock.DBusTestCase):

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
        # Set up an adapter_props and device.
        adapter_name = 'hci0'
        device_address = '11:22:33:44:55:66'
        device_alias = 'Peripheral Device'

        ml = GLib.MainLoop()

        self.dbusmock_bluez.AddAdapter(adapter_name, 'my-computer')
        self.dbusmock_bluez.AddDevice(
            adapter_name,
            device_address,
            device_alias)
        self.dbusmock_bluez.ConnectDevice()

    def tearDown(self):
        self.p_mock.terminate()
        self.p_mock.wait()

    def test_device_name(self):
        test_dev = Device('/org/bluez/hci0/dev_11_22_33_44_55_66')
        found_name = test_dev.name()
        # print('Connected? :', test_dev.connected())
        self.assertEqual(found_name, 'Peripheral Device')


if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
