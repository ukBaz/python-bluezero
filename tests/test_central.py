"""Automated testing of GATT functionality using unittest.mock."""
import sys
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants

adapter_props = tests.obj_data.full_ubits


def mock_get(iface, prop):
    if iface == 'org.bluez.Adapter1':
        return tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop]
    elif iface == 'org.bluez.Device1':
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_1C'][iface][prop]
    else:
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service002a'][iface][prop]


def mock_set(iface, prop, value):
    tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service002a'][iface][prop] = value


class TestBluezeroCentral(unittest.TestCase):
    """Test class to exercise Central Features."""

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
        from bluezero import central
        self.module_under_test = central
        self.path = '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service002a'
        self.adapter_path = '/org/bluez/hci0'
        self.dev_name = 'BBC micro:bit [zezet]'
        self.adapter_addr = '00:00:00:00:5A:AD'
        self.device_addr = 'E4:43:33:7E:54:1C'
        self.service_uuid = 'e95dd91d-251d-470a-a062-fa1922dfa9a8'

    def tearDown(self):
        self.module_patcher.stop()

    def test_service_uuid(self):
        """Test the central instantiation."""
        # Invoke the bluez GATT library to access the mock GATT service
        test_central = self.module_under_test.Central(adapter_addr=self.adapter_addr,
                                                      device_addr=self.device_addr)

        # Test for the UUID
        self.assertEqual(test_central.connected, True)

