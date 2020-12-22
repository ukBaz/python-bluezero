import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants


class TestDbusModuleCalls(unittest.TestCase):
    """
    Testing things that use the Dbus module
    """
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
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import async_tools
        self.module_under_test = async_tools.EventLoop()

    def tearDown(self):
        self.module_patcher.stop()

    def test_call_run(self):
        self.module_under_test.run()

    def test_call_quit(self):
        self.module_under_test.quit()
