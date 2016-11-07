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

        self.adapter_name = 'hci0'
        self.address = '11:22:33:44:55:66'
        self.alias = 'Peripheral Device'

        # Initialise an adapter
        self.ad_dpath = self.dbusmock_bluez.AddAdapter(self.adapter_name,
                                                       'my-computer')

        # Add a mock remote device
        self.dbusmock_bluez.AddDevice(self.adapter_name, self.address,
                                      self.alias)

        # Initialise a mock remote GATT device
        self.svc_dpath = self.dbusmock_bluez.AddGATT(self.adapter_name,
                                                     self.address, self.alias)

    def test_paths(self):
        """Test the adapter and service paths."""
        # Test for the adapter path
        self.assertEqual(self.ad_dpath, '/org/bluez/' + self.adapter_name)

        # Test for the service path
        srvc_dbus_path = '/org/bluez/hci0/dev_11_22_33_44_55_66/service0001'
        self.assertEqual(self.svc_dpath, srvc_dbus_path)

    def test_service_uuid(self):
        """Test the service UUID."""
        # Invoke the bluez GATT library to access the mock GATT service
        test_service = GATT.Service(self.svc_dpath)

        # Test for the UUID
        self.assertEqual(test_service.UUID, '180F')

    def test_service_device(self):
        """Test the service device path."""
        # Invoke the bluez GATT library to access the mock GATT service
        test_service = GATT.Service(self.svc_dpath)

        # Test for the device path
        dev_underscore = self.address.replace(':', '_').upper()
        dev_addr = '{0}/dev_{1}'.format(self.ad_dpath, dev_underscore)
        self.assertEqual(test_service.device, dev_addr)

    def test_service_primary(self):
        """Test the service primary flag."""
        # Invoke the bluez GATT library to access the mock GATT service
        test_service = GATT.Service(self.svc_dpath)

        # Test for the UUID
        self.assertEqual(test_service.primary, True)


if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
