"""Automated testing of GATT functionality using dbusmock."""

import subprocess
import sys
import unittest

import dbus
import dbusmock

from bluezero import GATT


class TestBluezeroService(dbusmock.DBusTestCase):
    """Test class to exercise (remote) GATT Service Features."""

    @classmethod
    def setUpClass(klass):
        """Initiate mock Bluez on a mock dbus."""
        klass.start_system_bus()
        klass.dbus_con = klass.get_dbus(True)
        (klass.p_mock, klass.obj_bluez) = klass.spawn_server_template(
            'bluez5', {}, stdout=subprocess.PIPE)

    def setUp(self):
        """Initialise the class for the tests."""
        self.obj_bluez.Reset()
        self.dbusmock = dbus.Interface(self.obj_bluez, dbusmock.MOCK_IFACE)
        self.dbusmock_bluez = dbus.Interface(self.obj_bluez, 'org.bluez.Mock')

    def test_service_uuid(self):
        """Test the service UUID."""
        adapter_name = 'hci0'
        address = '11:22:33:44:55:66'
        alias = 'Peripheral Device'

        # Initialise an adapter and ensure that it's on the right path
        path = self.dbusmock_bluez.AddAdapter(adapter_name, 'my-computer')
        self.assertEqual(path, '/org/bluez/' + adapter_name)

        # Add a mock remote device
        self.dbusmock_bluez.AddDevice(adapter_name, address, alias)

        # Initialise a mock remote GATT and ensure it's on the right path
        path = self.dbusmock_bluez.AddGATT(adapter_name, address, alias)
        srvc_dbus_path = '/org/bluez/hci0/dev_11_22_33_44_55_66/service0001'

        # Invoke the bluez GATT library to access the mock GATT service
        test_service = GATT.Service(srvc_dbus_path)

        # Test for the UUID
        found_name = test_service.UUID
        self.assertEqual(found_name, '180F')


if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
