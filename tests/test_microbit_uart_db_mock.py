import dbus
import dbusmock
import io
import logging
from pathlib import Path
import subprocess
from unittest import mock
from tests.mock_eventloop import MockAsync

# Module under test
from examples import microbit_uart


class TestAdapterExample(dbusmock.DBusTestCase):
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

    def test_run_uart_example(self):
        # Horrible hardcoded path that refers to characteristic defined in
        # microbit_data. Needs refactoring but this was quick to prove it
        # worked as a test methodology
        tx_path = '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028/char002b'
        rx_path = '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028/char0029'
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        path = self.dbusmock_bluez.AddDevice('hci0',
                                             'DD:02:02:02:02:02',
                                             'micro:bit[uart]')
        bus = self.get_dbus(True)
        dev_obj = bus.get_object('org.bluez', path)
        dev_mock = dbus.Interface(dev_obj, dbusmock.MOCK_IFACE)
        rx_obj = bus.get_object('org.bluez', rx_path)
        rx_mock = dbus.Interface(rx_obj, dbusmock.MOCK_IFACE)
        tx_obj = bus.get_object('org.bluez', tx_path)
        tx_mock = dbus.Interface(tx_obj, dbusmock.MOCK_IFACE)
        with mock.patch('bluezero.async_tools.EventLoop', MockAsync):
            with mock.patch('sys.stdout', new=io.StringIO()) as fake_out:
                microbit_uart.main('00:01:02:03:04:05', 'DD:02:02:02:02:02')

        # Check device calls
        device_calls = list(str(call[1]) for call in dev_mock.GetCalls())
        self.assertEqual(['Connect', 'Disconnect'], device_calls)
        # Check UART RX calls
        rx_calls = list(str(call[1]) for call in rx_mock.GetCalls())
        self.assertEqual(['WriteValue', 'WriteValue'], rx_calls)
        # Check UART TX calls
        tx_calls = list(str(call[1]) for call in tx_mock.GetCalls())
        self.assertEqual(['StartNotify'], tx_calls)
        # Check notification value is printed to screen
        self.assertEqual('Ping#\n', fake_out.getvalue())


