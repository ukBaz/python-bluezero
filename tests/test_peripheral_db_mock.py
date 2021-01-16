import dbus
import dbusmock
from pathlib import Path
import subprocess
from unittest import mock
from tests.mock_eventloop import MockAsync, run_pending_events

# Module under test
from examples import cpu_temperature


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

    def test_create_peripheral(self):
        # Test currently has limited value because the RegisterApplication
        # does not publish the peripheral with dbusmock
        # (dbusmock_templates/bluez_scan.py) so further testing cannot happen.

        # Add adapter
        path0 = self.dbusmock_bluez.AddAdapter('hci0', 'My-Peripheral')
        path1 = self.dbusmock_bluez.AddAdapter('hci1', 'My-Adapter')

        # Setup to monitor calls
        bus = self.get_dbus(True)
        peri_obj = bus.get_object('org.bluez', path1)
        peri_mock = dbus.Interface(peri_obj, dbusmock.MOCK_IFACE)
        adptr_obj = bus.get_object('org.bluez', path0)
        adptr_mock = dbus.Interface(adptr_obj, dbusmock.MOCK_IFACE)
        # Create
        with mock.patch('bluezero.async_tools.EventLoop.run', MockAsync.run):
            cpu_temperature.main(adapter_address='00:01:02:03:04:05')
        device_calls = list(str(call[1]) for call in peri_mock.GetCalls())
        adptr_calls = list(str(call[1]) for call in adptr_mock.GetCalls())
        self.assertEqual(['RegisterApplication'], adptr_calls)
        self.assertEqual([], device_calls)

