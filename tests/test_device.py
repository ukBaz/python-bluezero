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
        klass.start_system_bus()
        klass.dbus_con = klass.get_dbus(True)
        (klass.p_mock, klass.obj_bluez) = klass.spawn_server_template(
            'bluez5', {}, stdout=subprocess.PIPE)

    def setUp(self):
        self.obj_bluez.Reset()
        self.dbusmock = dbus.Interface(self.obj_bluez, dbusmock.MOCK_IFACE)
        self.dbusmock_bluez = dbus.Interface(self.obj_bluez, 'org.bluez.Mock')

    def tearDown(self):
        self.p_mock.terminate()
        self.p_mock.wait()

    def test_device_name(self):
        adapter_name = 'hci0'
        address = '11:22:33:44:55:66'
        alias = 'Peripheral Device'

        path = self.dbusmock_bluez.AddAdapter(adapter_name, 'my-computer')
        self.assertEqual(path, '/org/bluez/' + adapter_name)
        dongle = Adapter('/org/bluez/hci0')

        path = self.dbusmock_bluez.AddDevice('hci0',
                                             '11:22:33:44:55:66',
                                             'Peripheral Device')
        self.assertEqual(path,
                         '/org/bluez/' + adapter_name + '/dev_' +
                         address.replace(':', '_'))
        ble_dev = Device('/org/bluez/hci0/dev_11_22_33_44_55_66')
        found_name = ble_dev.name()
        self.assertEqual(found_name, 'Peripheral Device')


if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
