"""Class and methods that represent a Bluetooth Adapter.

Classes:

- Adapter -- Bluetooth Adapter Class

Methods:

- list_adapters -- List available adapters on the D-Bus interface
"""

from __future__ import absolute_import, print_function, unicode_literals

# D-Bus imports
import dbus
import dbus.mainloop.glib

# python-bluezero imports
from bluezero import constants

# Main eventloop import
try:
    from gi.repository import GLib as GObject
except ImportError:
    import gobject as GObject

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


# Initialise the mainloop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


def list_adapters():
    """List adapters that are available on the D-Bus."""
    paths = []
    bus = dbus.SystemBus()
    manager = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'),
        constants.DBUS_OM_IFACE)
    manager_obj = manager.GetManagedObjects()
    for path, ifaces in manager_obj.items():
        if constants.ADAPTER_INTERFACE in ifaces:
            paths.append(path)
    if len(paths) < 1:
        raise AdapterError('No Bluetooth adapter found')
    else:
        return paths


def interfaces_added(path, interfaces):
    if constants.DEVICE_INTERFACE in interfaces:
        logger.debug('Device added at {}'.format(path))


def properties_changed(interface, changed, invalidated, path):
    if constants.DEVICE_INTERFACE in interface:
        for prop in changed:
            logger.debug(
                '{}:{} Property {} new value {}'.format(interface,
                                                        path,
                                                        prop,
                                                        changed[prop]))


class AdapterError(Exception):
    pass


class Adapter:
    """Bluetooth Adapter Class.

    This class instantiates an object that interacts with the physical
    Bluetooth device via the D-Bus.

    :Example:

    >>> from bluezero import adapter
    >>> dongle = adapter.Adapter('/org/bluez/hci0')
    >>> dongle.powered = True

    """

    def __init__(self, adapter_path):
        """Default initialiser.

        Creates the D-Bus interface to the specified local Bluetooth
        adapter device.
        The DBus path must be specified.

        :param adapter_path: DBus path to the Bluetooth adapter.
        """
        self.bus = dbus.SystemBus()

        self.path = adapter_path
        self.adapter_object = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.path)
        self.adapter_methods = dbus.Interface(self.adapter_object,
                                              constants.ADAPTER_INTERFACE)

        self.adapter_props = dbus.Interface(self.adapter_object,
                                            dbus.PROPERTIES_IFACE)

        self._nearby_timeout = 10
        self._nearby_count = 0
        self.mainloop = GObject.MainLoop()

        self.bus.add_signal_receiver(interfaces_added,
                                     dbus_interface=constants.DBUS_OM_IFACE,
                                     signal_name='InterfacesAdded')

        self.bus.add_signal_receiver(properties_changed,
                                     dbus_interface=dbus.PROPERTIES_IFACE,
                                     signal_name='PropertiesChanged',
                                     arg0=constants.DEVICE_INTERFACE,
                                     path_keyword='path')

    @property
    def address(self):
        """Return the adapter MAC address."""
        return self.adapter_props.Get(constants.ADAPTER_INTERFACE, 'Address')

    @property
    def name(self):
        """Return the adapter name."""
        return self.adapter_props.Get(constants.ADAPTER_INTERFACE, 'Name')

    @property
    def bt_class(self):
        """Return the Bluetooth class of device."""
        return self.adapter_props.Get(constants.ADAPTER_INTERFACE, 'Class')

    @property
    def alias(self, new_alias=None):
        """Return or set the adapter alias.

        :param new_alias: (optional) the new alias of the adapter.
        """
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'Alias')

    @alias.setter
    def alias(self, new_alias):
        self.adapter_props.Set(
            constants.ADAPTER_INTERFACE, 'Alias', new_alias)

    def get_all(self):
        """Print all the Adapter attributes."""
        return self.adapter_props.GetAll(constants.ADAPTER_INTERFACE)

    @property
    def powered(self):
        """Get the power state of the Adapter."""
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'Powered')

    @powered.setter
    def powered(self, new_state):
        """Set the power state of the Adapter.

        :param new_state: boolean.
        """
        self.adapter_props.Set(
            constants.ADAPTER_INTERFACE, 'Powered', new_state)

    @property
    def pairable(self):
        """Get the pairable state of the Adapter."""
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'Pairable')

    @pairable.setter
    def pairable(self, new_state):
        """Set the pairable state of the Adapter."""
        self.adapter_props.Set(
            constants.ADAPTER_INTERFACE, 'Pairable', new_state)

    @property
    def pairabletimeout(self):
        """Set the pairable timeout of the Adapter."""
        return self.adapter_props.Get(constants.ADAPTER_INTERFACE,
                                      'PairableTimeout')

    @pairabletimeout.setter
    def pairabletimeout(self, new_timeout):
        self.adapter_props.Set(constants.ADAPTER_INTERFACE,
                               'PairableTimeout', new_timeout)

    @property
    def discoverable(self):
        """Get the discoverable state of the Adapter."""
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'Discoverable')

    @discoverable.setter
    def discoverable(self, new_state):
        self.adapter_props.Set(constants.ADAPTER_INTERFACE,
                               'Discoverable', new_state)

    @property
    def discoverabletimeout(self):
        """Get the discoverable timeout of the Adapter."""
        return self.adapter_props.Get(constants.ADAPTER_INTERFACE,
                                      'DiscoverableTimeout')

    @discoverabletimeout.setter
    def discoverabletimeout(self, new_timeout):
        self.adapter_props.Set(constants.ADAPTER_INTERFACE,
                               'DiscoverableTimeout', new_timeout)

    @property
    def discovering(self):
        """Return whether the adapter is discovering."""
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'Discovering')

    def _discovering_timeout(self):
        """Test to see if discovering should stop."""
        self._nearby_count += 1
        if self._nearby_count > self._nearby_timeout:
            self.stop_discovery()
            self.mainloop.quit()
            return False
        return True

    def nearby_discovery(self, timeout=10):
        """Start discovery of nearby Bluetooth devices."""
        self._nearby_timeout = timeout
        self._nearby_count = 0

        GObject.timeout_add(1000, self._discovering_timeout)
        self.adapter_methods.StartDiscovery()
        self.mainloop.run()

    def stop_discovery(self):
        """Stop scanning of nearby Bluetooth devices."""
        self.adapter_methods.StopDiscovery()
