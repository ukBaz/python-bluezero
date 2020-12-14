"""Automated testing of GATT functionality using unittest.mock."""
import sys
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants

adapter_props = tests.obj_data.full_ubits


def mock_get(iface, prop):
    if iface == 'org.bluez.Device1':
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_1C'][iface][prop]
    else:
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service002a'][iface][prop]


def mock_set(iface, prop, value):
    tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service002a'][iface][prop] = value


class TestBluezeroService(unittest.TestCase):
    """Test class to exercise (remote) GATT Service Features."""

    def setUp(self):
        """Initialise the class for the tests."""
        self.dbus_mock = MagicMock()
        self.mainloop_mock = MagicMock()
        self.gobject_mock = MagicMock()

        modules = {
            'dbus': self.dbus_mock,
            'dbus.exceptions': self.dbus_mock,
            'dbus.mainloop.glib': self.mainloop_mock,
            'gi.repository': self.gobject_mock,
        }
        self.dbus_mock.Interface.return_value.GetManagedObjects.return_value = tests.obj_data.full_ubits
        self.dbus_mock.Interface.return_value.Get = mock_get
        self.dbus_mock.Interface.return_value.Set = mock_set
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import GATT
        self.module_under_test = GATT
        self.path = '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service002a'
        self.adapter_path = '/org/bluez/hci0'
        self.dev_name = 'BBC micro:bit [zezet]'
        self.adapter_addr = '00:00:00:00:5A:AD'
        self.device_addr = 'E4:43:33:7E:54:1C'
        self.service_uuid = 'e95dd91d-251d-470a-a062-fa1922dfa9a8'

    def tearDown(self):
        self.module_patcher.stop()

    def test_service_uuid(self):
        """Test the service UUID."""
        # Invoke the bluez GATT library to access the mock GATT service
        test_service = self.module_under_test.Service(self.adapter_addr,
                                                      self.device_addr,
                                                      self.service_uuid)

        # Test for the UUID
        self.assertEqual(test_service.UUID, 'e95dd91d-251d-470a-a062-fa1922dfa9a8')

    def test_service_device(self):
        """Test the service device path."""
        # Invoke the bluez GATT library to access the mock GATT service
        test_service = self.module_under_test.Service(self.adapter_addr,
                                                      self.device_addr,
                                                      self.service_uuid)

        # Test for the device path
        dev_underscore = self.device_addr.replace(':', '_').upper()
        dev_addr = '{0}/dev_{1}'.format(self.adapter_path, dev_underscore)
        self.assertEqual(test_service.device, dev_addr)

    def test_service_primary(self):
        """Test the service primary flag."""
        # Invoke the bluez GATT library to access the mock GATT service
        test_service = self.module_under_test.Service(self.adapter_addr,
                                                      self.device_addr,
                                                      self.service_uuid)

        # Test for the UUID
        self.assertEqual(test_service.primary, True)


if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
