import dbus
import dbusmock
import io
from pathlib import Path
import subprocess
# from gi.repository import GLib
from unittest import mock, skip
from tests.mock_eventloop import MockAsync, run_pending_events

from examples import eddystone_scanner


class TestExampleScanner(dbusmock.DBusTestCase):
    """
    Test mocking bluetoothd
    TODO: Find how to end the spawned server at the end of tests
    Currently this is not happening at the end of tests and you have lots of
    processes hanging around. Currently the workaround is to do this manually
    on your system if this is an issue.
    kill $(ps aux  | grep "[d]bus-daemon.*dbusmock" | awk '{print $2}')
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
        cls.p_mock.terminate()
        cls.p_mock.wait()

    def test_scanner_eddy_url2(self):
        expected = 'Eddystone URL: https://www.bluetooth.com ↗ 8 ↘ -61'
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        with mock.patch('bluezero.async_tools.EventLoop.run', MockAsync.run):
            with mock.patch('sys.stdout', new=io.StringIO()) as fake_out:
                eddystone_scanner.main()
                self.assertIn(expected,
                              fake_out.getvalue())

