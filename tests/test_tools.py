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

        modules = {
            'dbus': self.dbus_mock,
            'dbus.mainloop.glib': self.mainloop_mock,
            'gi.repository': self.gobject_mock,
        }
        self.dbus_mock.Interface.return_value.GetManagedObjects.return_value = tests.obj_data.full_ubits
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import tools
        self.module_under_test = tools

    def tearDown(self):
        self.module_patcher.stop()

    def test_NoSuffix(self):
        self.assertEqual(
            self.module_under_test.url_to_advert(
                'http://camjam.me/', 0x10, 0x00),
            [0x10, 0x00, 0x02, 0x63, 0x61, 0x6D, 0x6A,
             0x61, 0x6D, 0x2E, 0x6D, 0x65, 0x2F])

    def test_WithSuffix(self):
        self.assertEqual(
            self.module_under_test.url_to_advert(
                'https://www.google.com', 0x10, 0x00),
            [0x10, 0x00, 0x01, 0x67, 0x6f,
             0x6f, 0x67, 0x6c, 0x65, 0x07])

    def test_PostSuffix(self):
        self.assertEqual(
            self.module_under_test.url_to_advert(
                'http://www.csr.com/about', 0x10, 0x00),
            [0x10, 0x00, 0x00, 0x63, 0x73, 0x72,
             0x00, 0x61, 0x62, 0x6f, 0x75, 0x74])

    def test_IntToUint32_with_zeros(self):
        little_endian = self.module_under_test.int_to_uint32(2094)
        self.assertListEqual(little_endian, [0x2E, 0x08, 0x00, 0x00])

    def test_IntToUint32_all_full(self):
        little_endian = self.module_under_test.int_to_uint32(305419896)
        self.assertListEqual(little_endian, [0x78, 0x56, 0x34, 0x12])

    def test_IntToUint16(self):
        little_endian = self.module_under_test.int_to_uint16(43733)
        self.assertListEqual(little_endian, [0xD5, 0xAA])

    def test_Sint16ToInt(self):
        result = self.module_under_test.int_to_uint16(0b1111111011101111)
        self.assertEqual(result, [0xEF, 0xFE])

    def test_bytes_to_xyz(self):
        # result = self.module_under_test.bytes_to_xyz([32, 176, 40,239, 96, 84])
        result = self.module_under_test.bytes_to_xyz([0x20, 0x00, 0xD0, 0x00, 0x20, 0xFC])
        self.assertEqual(result, [0.032, 0.208, -0.992])

if __name__ == '__main__':
    unittest.main()
