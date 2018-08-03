# Main eventloop import
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


class EventLoop:
    # def generic_error_cb(self, error):
    #     """Generic Error Callback function."""
    #     logger.error('D-Bus call failed: ' + str(error))
    #     self.mainloop.quit()

    # def __new__(cls):
    #     return object.__new__(cls)

    def __init__(self):
        self.mainloop = GObject.MainLoop()

    def run(self):
        self.mainloop.run()

    def quit(self):
        self.mainloop.quit()

    def is_running(self):
        self.mainloop.is_running()

    def add_timer(self, time, callback):
        GObject.timeout_add(time, callback)
