import dbus
import dbusmock
import io
from pathlib import Path
import subprocess
from unittest import mock
from gi.repository import GLib

# Module under test
from examples import adapter_example


class MockAsync:

    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = GLib.MainLoop()

    def run(self):
        main_context = GLib.MainContext.default()
        while main_context.pending():
            main_context.iteration(False)


class TestAdapterExample(dbusmock.DBusTestCase):
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
        template = str(here.joinpath('dbusmock_bluez_scan.py'))
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

    def test_on_device_found(self):

        class ForTest:
            found_address = None

            @classmethod
            def new_dev(cls, device):
                cls.found_address = device.address

        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')

        with mock.patch('bluezero.async_tools.EventLoop', MockAsync):
            with mock.patch('sys.stdout', new=io.StringIO()) as fake_out:
                adapter_example.main()
                self.assertIn('address:  00:01:02:03:04:05',
                              fake_out.getvalue())
