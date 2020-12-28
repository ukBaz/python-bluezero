import dbus
from gi.repository import GLib


def run_pending_events():
    """
    Iterate event loop until all pending events are cleared
    """
    main_context = GLib.MainContext.default()
    while main_context.pending():
        main_context.iteration(False)


class MockAsync:

    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = GLib.MainLoop()

    def run(self):
        main_context = GLib.MainContext.default()
        while main_context.pending():
            main_context.iteration(False)

    def quit(self):
        self.mainloop.quit()
