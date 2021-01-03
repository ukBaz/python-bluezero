"""
Collection of functions to work with the GLib Event Loop
"""
# Main eventloop import
import dbus
import dbus.mainloop.glib
from gi.repository import GLib

from bluezero import tools

logger = tools.create_module_logger(__name__)


def add_timer_ms(time, callback, data=None):
    """Call given callback every x milliseconds"""
    if data:
        GLib.timeout_add(time, callback, data)
    else:
        GLib.timeout_add(time, callback)


def add_timer_seconds(time, callback, data=None):
    """Call given callback every x seconds"""
    if data:
        GLib.timeout_add_seconds(time, callback, data)
    else:
        GLib.timeout_add_seconds(time, callback)


class EventLoop:
    """Facade class to help with using GLib event loop"""
    # def generic_error_cb(self, error):
    #     """Generic Error Callback function."""
    #     logger.error('D-Bus call failed: ' + str(error))
    #     self.mainloop.quit()

    # def __new__(cls):
    #     return object.__new__(cls)

    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = GLib.MainLoop()

    def run(self):
        """Run event loop"""
        self.mainloop.run()

    def quit(self):
        """Stop event loop"""
        self.mainloop.quit()

    def is_running(self):
        """Check if event loop is running"""
        self.mainloop.is_running()
