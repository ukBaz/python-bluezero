import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants


def mock_get(iface, prop):
    return tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop]


def mock_set(iface, prop, value):
    tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop] = value


class TestBluezeroMicrobit(unittest.TestCase):

    def setUp(self):
        """
        Patch the DBus module
        :return:
        """
        self.dbus_mock = MagicMock()
        self.dbus_exception_mock = MagicMock()
        self.dbus_service_mock = MagicMock()
        self.mainloop_mock = MagicMock()
        self.gobject_mock = MagicMock()

        modules = {
            'dbus': self.dbus_mock,
            'dbus.exceptions': self.dbus_exception_mock,
            'dbus.service': self.dbus_service_mock,
            'dbus.mainloop.glib': self.mainloop_mock,
            'gi.repository': self.gobject_mock,
        }
        self.dbus_mock.Interface.return_value.GetManagedObjects.return_value = tests.obj_data.full_ubits
        self.dbus_mock.Interface.return_value.Get = mock_get
        self.dbus_mock.Interface.return_value.Set = mock_set
        self.dbus_mock.SystemBus = MagicMock()
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import localGATT
        self.module_under_test = localGATT

    def tearDown(self):
        self.module_patcher.stop()

    def test_load(self):
        my_blinkt = self.module_under_test.Service(service_id=1, UUID='2404',
                                                   primary=True)
