import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants


def mock_get(iface, prop):
    return tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop]


def mock_set(iface, prop, value):
    tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop] = value


class TestBluezeroAdapter(unittest.TestCase):

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
        self.dbus_mock.Interface.return_value.Get = mock_get
        self.dbus_mock.Interface.return_value.Set = mock_set
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import adapter
        self.module_under_test = adapter
        self.adapter_device = 'hci0'
        self.adapter_name = 'linaro-alip'
        self.path = '/org/bluez/hci0'

    def tearDown(self):
        self.module_patcher.stop()

    def test_list_adapters(self):
        adapters = self.module_under_test.list_adapters()
        self.assertListEqual(['/org/bluez/hci0'], adapters)

    def test_adapter_address(self):
        dongle = self.module_under_test.Adapter(self.path)
        self.assertEqual(dongle.address, '00:00:00:00:5A:AD')

    def test_adapter_name(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        self.assertEqual(dongle.name, self.adapter_name)

    def test_adapter_alias(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        self.assertEqual(dongle.alias, self.adapter_name)

    def test_adapter_alias_write(self):
        dev_name = 'my-test-dev'
        dongle = self.module_under_test.Adapter(self.path)
        # test
        dongle.alias = dev_name
        self.assertEqual(dongle.alias, dev_name)

    def test_class(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        self.assertEqual(dongle.bt_class, 4980736)

    def test_adapter_power(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        self.assertEqual(dongle.powered, 1)

    def test_adapter_power_write(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        dongle.powered = 0
        self.assertEqual(dongle.powered, False)

    def test_adapter_discoverable(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        self.assertEqual(dongle.discoverable, False)

    def test_adapter_discoverable_write(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        dongle.discoverable = 1
        self.assertEqual(dongle.discoverable, True)

    def test_adapter_pairable(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        self.assertEqual(dongle.pairable, 1)

    def test_adapter_pairable_write(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        dongle.pairable = 0
        self.assertEqual(dongle.pairable, 0)

    def test_adapter_pairabletimeout(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        self.assertEqual(dongle.pairabletimeout, 0)

    def test_adapter_pairabletimeout_write(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        dongle.pairabletimeout = 220
        self.assertEqual(dongle.pairabletimeout, 220)

    def test_adapter_discoverabletimeout(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        self.assertEqual(dongle.discoverabletimeout, 180)

    def test_adapter_discoverabletimeout_write(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        dongle.discoverabletimeout = 220
        self.assertEqual(dongle.discoverabletimeout, 220)

    def test_adapter_discovering(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        self.assertEqual(dongle.discovering, False)

    @unittest.skip('mock of discovery not implemented')
    def test_start_discovery(self):
        dongle = self.module_under_test.Adapter(self.path)
        # test
        dongle.nearby_discovery()
        self.assertEqual(dongle.discovering, 1)


if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
