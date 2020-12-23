import dbus
import dbusmock
import io
from pathlib import Path
from pprint import pprint
import subprocess
from unittest import mock
from gi.repository import GLib

# Module under test
from examples import eddystone_url_beacon


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

    def test_eddystone_url_beacon(self):
        # TODO: A very light test at the moment. Needs to do more checking
        path = self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')
        # self.mngr = dbus.Interface(self.dbus_con.get_object('org.bluez', '/'),
        #                            'org.freedesktop.DBus.ObjectManager')
        # pprint(self.mngr.GetManagedObjects())

        dongle = self.dbus_con.get_object('org.bluez', path)
        self.assertFalse(dongle.Get('org.bluez.Adapter1', 'Discoverable'))
        with mock.patch('bluezero.async_tools.EventLoop', MockAsync):
            eddystone_url_beacon.main()
        # print(self.dbusmock_bluez.GetCalls())

        self.assertTrue(dongle.Get('org.bluez.Adapter1', 'Discoverable'))
        # pprint(self.mngr.GetManagedObjects())
