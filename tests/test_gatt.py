import subprocess
import sys
import unittest

import dbus
import dbusmock

from bluezero.adapter import Adapter
from bluezero.device import Device
from bluezero import GATT


class TestBluezeroService(dbusmock.DBusTestCase):

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

    def test_service_uuid(self):
        adapter_name = 'hci0'
        address = '11:22:33:44:55:66'
        alias = 'Peripheral Device'

        path = self.dbusmock_bluez.AddAdapter(adapter_name, 'my-computer')
        self.assertEqual(path, '/org/bluez/' + adapter_name)
        dongle = Adapter('/org/bluez/hci0')

        dev_path = self.dbusmock_bluez.AddDevice('hci0',
                                                 '11:22:33:44:55:66',
                                                 'Peripheral Device')

        path = self.dbusmock_bluez.AddGATT('hci0',
                                           '11:22:33:44:55:66',
                                           'Peripheral Device')
        srvc_dbus_path = '/org/bluez/hci0/dev_11_22_33_44_55_66/service0001'
        test_service = GATT.Service(srvc_dbus_path)
        test_device = Device('/org/bluez/hci0/dev_11_22_33_44_55_66')
        found_name = test_service.UUID
        self.assertEqual(found_name, '180F')


if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
