# Main eventloop import
from gi.repository import GLib
import logging

from bluezero import tools

logger = tools.create_module_logger(__name__)


class EventLoop:
    # def generic_error_cb(self, error):
    #     """Generic Error Callback function."""
    #     logger.error('D-Bus call failed: ' + str(error))
    #     self.mainloop.quit()

    # def __new__(cls):
    #     return object.__new__(cls)

    def __init__(self):
        self.mainloop = GLib.MainLoop()

    def run(self):
        self.mainloop.run()

    def quit(self):
        self.mainloop.quit()

    def is_running(self):
        self.mainloop.is_running()

    @staticmethod
    def add_timer(time, callback):
        GLib.timeout_add(time, callback)
