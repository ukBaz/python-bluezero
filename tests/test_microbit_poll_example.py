import dbus
import dbusmock
import io
from pathlib import Path
import subprocess
# from gi.repository import GLib
from unittest import mock, skip
from tests.mock_eventloop import MockAsync, run_pending_events

from examples import microbit_poll


class TestExampleScanner(dbusmock.DBusTestCase):
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

    def test_add_microbit(self):
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        path = self.dbusmock_bluez.AddDevice('hci0', 'E9:06:4D:45:FC:8D', '')
        dev = self.dbus_con.get_object('org.bluez', path)
        name = dev.Get('org.bluez.Device1', 'Name')
        alias = dev.Get('org.bluez.Device1', 'Alias')
        self.assertIn('micro:bit', name)
        self.assertIn('micro:bit', alias)

    def test_connect_microbit(self):
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        path = self.dbusmock_bluez.AddDevice('hci0', 'E9:06:4D:45:FC:8D', '')
        dev = self.dbus_con.get_object('org.bluez', path)
        self.assertFalse(dev.Get('org.bluez.Device1', 'Connected'))
        self.dbusmock_bluez.ConnectDevice('hci0', 'E9:06:4D:45:FC:8D')
        self.assertTrue(dev.Get('org.bluez.Device1', 'Connected'))

    @skip("Poll test is timing out")
    def test_poll_example(self):
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        path = self.dbusmock_bluez.AddDevice('hci0', 'E9:06:4D:45:FC:8D', '')
        # self.dbusmock_bluez.ConnectMicroBit()
        # path = dbus.ObjectPath('/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service003c')
        # srvc_props = dbus.Dictionary({'UUID': 'e95d6100-251d-470a-a062-fa1922dfa9a8',
        #                               'Device': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D',
        #                               'Primary': True}, signature='sv')
        # self.dbusmock_bluez.AddGattService(path, srvc_props)
        # path = dbus.ObjectPath('/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service003c/char0040')
        # chrc_props = dbus.Dictionary({
        #     'UUID': 'e95d1b25-251d-470a-a062-fa1922dfa9a8',
        #     'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service003c',
        #     'Value': [], 'Flags': ['read', 'write']}, signature='sv')
        # chrc_props['Value'] = dbus.Array(chrc_props['Value'], signature='y')
        # self.dbusmock_bluez.AddGattCharacteristic(path, chrc_props)
        with mock.patch('time.sleep', return_value=None):
            microbit_poll.main()
