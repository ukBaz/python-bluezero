import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants


class TestDbusModuleCalls(unittest.TestCase):
    """
    Testing things that use the Dbus module
    """
    def setUp(self):
        """
        Patch the DBus module
        :return:
        """
        self.dbus_mock = MagicMock()
        self.mainloop_mock = MagicMock()
        self.gobject_mock = MagicMock()
        self.process_mock = MagicMock()

        modules = {
            'dbus': self.dbus_mock,
            'dbus.mainloop.glib': self.mainloop_mock,
            'gi.repository': self.gobject_mock,
            'subprocess': self.process_mock
        }
        self.dbus_mock.Interface.return_value.GetManagedObjects.return_value = tests.obj_data.full_ubits

        self.process_mock.Popen.return_value.communicate.return_value = (b'5.43\n', None)
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import dbus_tools
        self.module_under_test = dbus_tools

    def tearDown(self):
        self.module_patcher.stop()

    def test_uuid_path_gatt(self):
        dbus_full_path = self.module_under_test.get_dbus_path(adapter='00:00:00:00:5A:AD',
                                                              device='F7:17:E4:09:C0:C6',
                                                              service='e95df2d8-251d-470a-a062-fa1922dfa9a8',
                                                              characteristic='e95d9715-251d-470a-a062-fa1922dfa9a8',
                                                              descriptor='00002902-0000-1000-8000-00805f9b34fb')
        expected_result = '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0031/char0035/desc0037'
        self.assertEqual(dbus_full_path, expected_result)

    def test_bad_pathh(self):
        self.assertRaises(ValueError,
                          self.module_under_test.get_dbus_path,
                          adapter='00:00:00:00:5A:C6',
                          device='F7:17:E4:09:C0:XX',
                          service='e95df2d8-251d-470a-a062-fa1922dfa9a8')

    def test_get_iface_from_path(self):
        my_iface = self.module_under_test.get_iface(adapter='00:00:00:00:5A:AD',
                                                    device='F7:17:E4:09:C0:C6',
                                                    service='e95df2d8-251d-470a-a062-fa1922dfa9a8',
                                                    characteristic='e95d9715-251d-470a-a062-fa1922dfa9a8',
                                                    descriptor='00002902-0000-1000-8000-00805f9b34fb')
        self.assertEqual(constants.GATT_DESC_IFACE, my_iface)

    def test_profile_path(self):
        my_iface = self.module_under_test.get_profile_path(adapter='00:00:00:00:5A:AD',
                                                           device='F7:17:E4:09:C0:C6',
                                                           profile='e95df2d8-251d-470a-a062-fa1922dfa9a8')
        self.assertEqual(None, my_iface)


    def test_bluez_version(self):
        bluez_ver = self.module_under_test.bluez_version()
        self.assertEqual('5.43', bluez_ver)

if __name__ == '__main__':
    unittest.main()
