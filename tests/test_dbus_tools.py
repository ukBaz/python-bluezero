import subprocess
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants


class TestDbusModuleCalls(unittest.TestCase):
    """
    Testing things that use the Dbus module
    """
    experimental = True
    bluetooth_service_experimental = b'\xe2\x97\x8f bluetooth.service - Bluetooth service\n   Loaded: loaded (/lib/systemd/system/bluetooth.service; enabled; vendor preset: enabled)\n   Active: active (running) since Fri 2017-10-13 21:48:58 UTC; 1 day 23h ago\n     Docs: man:bluetoothd(8)\n Main PID: 530 (bluetoothd)\n   Status: "Running"\n   CGroup: /system.slice/bluetooth.service\n           \xe2\x94\x94\xe2\x94\x80530 /usr/lib/bluetooth/bluetoothd --experimental\n\nOct 13 21:48:58 RPi3 systemd[1]: Starting Bluetooth service...\nOct 13 21:48:58 RPi3 bluetoothd[530]: Bluetooth daemon 5.43\nOct 13 21:48:58 RPi3 systemd[1]: Started Bluetooth service.\nOct 13 21:48:58 RPi3 bluetoothd[530]: Bluetooth management interface 1.14 initialized\nOct 13 21:48:58 RPi3 bluetoothd[530]: Failed to obtain handles for "Service Changed" characteristic\nOct 13 21:48:58 RPi3 bluetoothd[530]: Endpoint registered: sender=:1.10 path=/MediaEndpoint/A2DPSource\nOct 13 21:48:58 RPi3 bluetoothd[530]: Endpoint registered: sender=:1.10 path=/MediaEndpoint/A2DPSink\n'
    bluetooth_service_normal = b'\xe2\x97\x8f bluetooth.service - Bluetooth service\n   Loaded: loaded (/lib/systemd/system/bluetooth.service; enabled; vendor preset: enabled)\n   Active: active (running) since Fri 2017-10-13 21:48:58 UTC; 1 day 23h ago\n     Docs: man:bluetoothd(8)\n Main PID: 530 (bluetoothd)\n   Status: "Running"\n   CGroup: /system.slice/bluetooth.service\n           \xe2\x94\x94\xe2\x94\x80530 /usr/lib/bluetooth/bluetoothd\n\nOct 13 21:48:58 RPi3 systemd[1]: Starting Bluetooth service...\nOct 13 21:48:58 RPi3 bluetoothd[530]: Bluetooth daemon 5.43\nOct 13 21:48:58 RPi3 systemd[1]: Started Bluetooth service.\nOct 13 21:48:58 RPi3 bluetoothd[530]: Bluetooth management interface 1.14 initialized\nOct 13 21:48:58 RPi3 bluetoothd[530]: Failed to obtain handles for "Service Changed" characteristic\nOct 13 21:48:58 RPi3 bluetoothd[530]: Endpoint registered: sender=:1.10 path=/MediaEndpoint/A2DPSource\nOct 13 21:48:58 RPi3 bluetoothd[530]: Endpoint registered: sender=:1.10 path=/MediaEndpoint/A2DPSink\n'

    def get_bluetooth_service(self, cmd, shell):
        if TestDbusModuleCalls.experimental:
            return TestDbusModuleCalls.bluetooth_service_experimental
        else:
            return TestDbusModuleCalls.bluetooth_service_normal

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
        self.process_mock.check_output = self.get_bluetooth_service
        self.process_mock.run.return_value = subprocess.CompletedProcess(
            args=['bluetoothctl', '-v'], returncode=0, stdout=b'bluetoothctl: 5.53\n', stderr=b'')
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

    def test_bad_path(self):
        path_found = self.module_under_test.get_dbus_path(adapter='00:00:00:00:5A:C6',
                                                          device='F7:17:E4:09:C0:XX',
                                                          service='e95df2d8-251d-470a-a062-fa1922dfa9a8')
        expected_path = None
        self.assertEqual(path_found, expected_path)

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
        self.assertEqual('5.53', bluez_ver)

    def test_bluez_service_experimental(self):
        TestDbusModuleCalls.experimental = True
        bluez_exper = self.module_under_test.bluez_experimental_mode()
        self.assertTrue(bluez_exper)

    def test_bluez_service_normal(self):
        TestDbusModuleCalls.experimental = False
        bluez_exper = self.module_under_test.bluez_experimental_mode()
        self.assertFalse(bluez_exper)

    def test_get_device_address_from_dbus_path(self):
        """
        Get mac address fromo any given dbus_path that includes
        "dev_xx_xx_xx_xx"
        """
        test_data = [
            ['/org/bluez/hci0/dev_EB_F6_95_27_84_A0', 'EB:F6:95:27:84:A0'],
            ['/org/bluez/hci0', ''],
            ['/org/bluez/hci0/dev_EB_F6_95_27_84_A0/player0',
             'EB:F6:95:27:84:A0']
        ]
        for i in range(0, len(test_data)):
            with self.subTest(i=i):
                self.assertEqual(
                    test_data[i][1],
                    self.module_under_test.get_device_address_from_dbus_path(
                        test_data[i][0]
                    ))

    def test_mac_addr_deprecated(self):
        with patch('logging.Logger.warning') as logger:
            self.module_under_test.get_mac_addr_from_dbus_path(
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0')
            logger.assert_called_once_with('get_mac_addr_from_dbus_path has '
                                           'been deprecated and has been '
                                           'replaced with '
                                           'get_device_address_from_dbus_path')

    def test_get_device_address(self):
        expected = [{'E4:43:33:7E:54:1C': 'BBC micro:bit [pugit]'}]
        result = self.module_under_test.get_device_addresses('pugit')
        self.assertTrue(isinstance(result, list))
        self.assertDictEqual(expected[0], result[0])


if __name__ == '__main__':
    unittest.main()
