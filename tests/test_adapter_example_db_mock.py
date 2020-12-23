import dbus
import dbusmock
import io
from pathlib import Path
import subprocess
from unittest import mock
from tests.mock_eventloop import MockAsync

# Module under test
from examples import adapter_example


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
