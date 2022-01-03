"""
Collection of functions to work with the GLib Event Loop
"""
# Main eventloop import
# import dbus
# import dbus.mainloop.glib

from gi.repository import Gio, GLib

from bluezero import tools, gio_dbus

logger = tools.create_module_logger(__name__)


def add_timer_ms(time, callback, data=None):
    """Call given callback every x milliseconds"""
    if data:
        GLib.timeout_add(time, callback, data)
    else:
        GLib.timeout_add(time, callback)


def add_timer_seconds(time, callback, *data):
    """Call given callback every x seconds"""
    if data:
        GLib.timeout_add_seconds(time, callback, *data)
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


class BluezeroRunner:
    def __init__(self):
        print('BluezeroRunner init')
        self.mainloop = GLib.MainLoop()
        self.bluez = gio_dbus.BluezDBusClient()

        self.on_start()
        GLib.idle_add(self.forever)
        self.bluez.on_object_added = self.on_device_added
        self.bluez.on_device_removed = self.on_device_removed
        self.bluez.on_properties_changed = self.on_properties_changed
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            self.mainloop.quit()

    def on_start(self):
        pass

    def forever(self):
        pass

    def on_device_added(self, dbus_object: Gio.DBusObject):
        pass

    def on_device_removed(self, dbus_object: Gio.DBusObject):
        pass

    def on_properties_changed(
            self, object_proxy, iface_name, properties_changed,
            properties_removed):
        pass

    def exit(self):
        self.mainloop.quit()
