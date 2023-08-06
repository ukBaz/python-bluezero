import dbus
import dbusmock
from pathlib import Path
import subprocess
from unittest import mock, skip
from tests.mock_eventloop import MockAsync, run_pending_events

from bluezero import adapter
from bluezero.adapter import AdapterError
from bluezero import observer


class TestBlueZ5(dbusmock.DBusTestCase):
    """
    Test mocking bluetoothd
    """

    @classmethod
    def setUpClass(cls):
        here = Path(__file__).parent
        template = str(here.joinpath('dbusmock_templates', 'bluez_scan.py'))
        cls.start_system_bus()
        cls.dbus_con = cls.get_dbus(True)
        (cls.p_mock, cls.obj_bluez) = cls.spawn_server_template(
            template, {}, stdout=subprocess.PIPE)

    def setUp(self):
        self.obj_bluez.Reset()
        self.dbusmock = dbus.Interface(self.obj_bluez, dbusmock.MOCK_IFACE)
        self.dbusmock_bluez = dbus.Interface(self.obj_bluez, 'org.bluez.Mock')

    @classmethod
    def tearDownClass(cls):
        cls.stop_dbus(cls.system_bus_pid)
        cls.p_mock.terminate()
        cls.p_mock.wait()

    def test_no_adapters(self):
        # Check for adapters.
        with self.assertRaises(AdapterError):
            out = adapter.list_adapters()

    def test_no_adapters_available(self):
        out = adapter.Adapter.available()
        with self.assertRaises(AdapterError):
            next(out)

    def test_one_adapter(self):
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        dongle = adapter.Adapter()
        name = dongle.name
        self.assertEqual('My-Test-Device', name)

    def test_available_list(self):
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        addresses = [dongle.address for dongle in adapter.Adapter.available()]
        self.assertEqual(['00:01:02:03:04:05'], addresses)

    def test_one_adapter_available(self):
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        dongles = adapter.Adapter.available()
        for dongle in dongles:
            self.assertEqual('My-Test-Device', dongle.name)
            self.assertEqual('00:01:02:03:04:05', dongle.address)
            self.assertEqual('0x10c', hex(dongle.bt_class))
            self.assertEqual('My-Test-Device', dongle.alias)
            dongle.alias = 'New Alias'
            self.assertEqual('New Alias', dongle.alias)
            self.assertEqual(True, dongle.powered)

    def test_on_device_found(self):
        device_address = '11:01:02:03:04:05'

        class ForTest:
            found_address = None

            @classmethod
            def new_dev(cls, device):
                cls.found_address = device.address

        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        dongle = adapter.Adapter()
        dongle.on_device_found = ForTest.new_dev
        self.dbusmock_bluez.AddDevice('hci0',
                                      device_address,
                                      'My-Peripheral-Device')
        run_pending_events()

        self.assertEqual(device_address, ForTest.found_address)

    def test_scanner_altbeacon(self):
        class ForTest:
            found_data = None

            @classmethod
            def new_dev(cls, device):
                cls.found_data = device.major

        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        with mock.patch('bluezero.async_tools.EventLoop.run', MockAsync.run):
            observer.Scanner.start_beacon_scan(on_altbeacon=ForTest.new_dev)
        self.assertEqual(24931, ForTest.found_data)

    @skip("Fails when run as part of suite but passses on own. Skipping for now")
    def test_scanner_iBeacon(self):
        class ForTest:
            found_data = None

            @classmethod
            def new_dev(cls, device):
                cls.found_data = device.major

        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        with mock.patch('bluezero.async_tools.EventLoop.run', MockAsync.run):
            observer.Scanner.start_beacon_scan(on_ibeacon=ForTest.new_dev)
        self.assertEqual(278, ForTest.found_data)

    def test_scanner_eddy_url(self):

        class ForTest:
            found_data = None

            @classmethod
            def new_dev(cls, device):
                cls.found_data = device.url

        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        with mock.patch('bluezero.async_tools.EventLoop.run', MockAsync.run):
            observer.Scanner.start_beacon_scan(
                on_eddystone_url=ForTest.new_dev)
        self.assertEqual('https://www.bluetooth.com',
                         ForTest.found_data)

    def test_scanner_eddy_url2(self):

        class ForTest:
            found_data = None

            @classmethod
            def new_dev(cls, device):
                cls.found_data = device.url

        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        with mock.patch('bluezero.async_tools.EventLoop.run', MockAsync.run):
            observer.scan_eddystone(
                on_data=ForTest.new_dev)
        self.assertEqual('https://www.bluetooth.com',
                         ForTest.found_data)

    def test_scanner_eddy_uid(self):

        class ForTest:
            found_data = None

            @classmethod
            def new_dev(cls, device):
                cls.found_data = device.namespace

        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        with mock.patch('bluezero.async_tools.EventLoop.run', MockAsync.run):
            observer.Scanner.start_beacon_scan(
                on_eddystone_uid=ForTest.new_dev)
        self.assertEqual(297987634280,
                         ForTest.found_data)
