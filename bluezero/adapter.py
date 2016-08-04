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
from gi.repository import GLib


# Initialise the mainloop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


def list_adapters():
    """List adapters that are available on the D-Bus."""
    paths = []
    bus = dbus.SystemBus()
    manager = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'),
        constants.DBUS_OM_IFACE)
    manager_obj = manager.GetManagedObjects()
    for path, ifaces in manager_obj.items():
        adapter = ifaces.get(constants.ADAPTER_INTERFACE)
        if adapter is None:
            continue
        else:
            obj = bus.get_object(constants.BLUEZ_SERVICE_NAME, path)
            paths.append(
                dbus.Interface(obj, constants.ADAPTER_INTERFACE).object_path)
    if len(paths) < 1:
        raise Exception('No Bluetooth adapter found')
    else:
        return paths


class Adapter:
    """Bluetooth Adapter Class.

    This class instantiates an object that interacts with the physical
    Bluetooth device via the D-Bus.

    :Example:

    >>> from bluezero import adapter
    >>> dongle = adapter.Adapter('/org/bluez/hci0')
    >>> dongle.powered('on')

    """

    def __init__(self, adapter_path):
        """Default initialiser.

        Creates the D-Bus interface to the specified local Bluetooth
        adapter device.
        The DBus path must be specified.

        :param dev_id: DBus path to the Bluetooth adapter.
        """
        self.bus = dbus.SystemBus()

        self.adapter_path = adapter_path
        self.adapter_object = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.adapter_path)
        self.adapter_methods = dbus.Interface(self.adapter_object,
                                              constants.ADAPTER_INTERFACE)

        self.adapter_props = dbus.Interface(
            self.bus.get_object(
                'org.bluez',
                self.adapter_path),
            'org.freedesktop.DBus.Properties'
        )
        self._nearby_timeout = 10
        self._nearby_count = 0
        self.mainloop = GLib.MainLoop()

    def address(self):
        """Return the adapter MAC address."""
        return self.adapter_props.Get(constants.ADAPTER_INTERFACE, 'Address')

    def name(self):
        """Return the adapter name."""
        return self.adapter_props.Get(constants.ADAPTER_INTERFACE, 'Name')

    def bt_class(self):
        """Return the Bluetooth class of device."""
        return self.adapter_props.Get(constants.ADAPTER_INTERFACE, 'Class')

    def alias(self, new_alias=None):
        """Return or set the adapter alias.

        :param new_alias: (optional) the new alias of the adapter.
        """
        if new_alias is None:
            return self.adapter_props.Get(
                constants.ADAPTER_INTERFACE, 'Alias')
        else:
            self.adapter_props.Set(
                constants.ADAPTER_INTERFACE, 'Alias', new_alias)

    def info(self):
        """Return a dictionary of all the Adapter attributes."""
        adapters = {}
        om = dbus.Interface(
            self.bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'),
            constants.DBUS_OM_IFACE)
        objects = om.GetManagedObjects()
        for path, interfaces in objects.items():
            if constants.ADAPTER_INTERFACE not in interfaces:
                continue

            # print(' [ %s ]' % (path))

            props = interfaces[constants.ADAPTER_INTERFACE]

            for (key, value) in props.items():
                if key == 'Class':
                    print('\t{0} = 0x{1:06x}'.format(key, value))
                    adapters[key] = '0x{0:06x}'.format(value)
                else:
                    print('\t{0} = {1}'.format(key, value))
                    adapters[key] = '{0}'.format(value)
            # print('Returning')
            return adapters

    def powered(self, new_state=None):
        """Get or set the power state of the Adapter.

        :param new_state: (optional) on or off changes the state.

        Whether changed or not, the power state is returned.
        """
        powered = ''
        if new_state is None:
            powered = self.adapter_props.Get(
                constants.ADAPTER_INTERFACE, 'Powered')
        else:
            if new_state == 'on':
                value = dbus.Boolean(1)
            elif new_state == 'off':
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(new_state)
            self.adapter_props.Set(
                constants.ADAPTER_INTERFACE, 'Powered', value)
            powered = self.adapter_props.Get(
                constants.ADAPTER_INTERFACE, 'Powered')
        return powered

    def pairable(self, new_state=None):
        """Get or set the pairable state of the Adapter.

        :param new_state: (optional) on or off changes the state.

        Whether changed or not, the pairable state is returned.
        """
        if new_state is None:
            pairable = self.adapter_props.Get(
                constants.ADAPTER_INTERFACE, 'Pairable')
        else:
            if new_state == 'on':
                value = dbus.Boolean(1)
            elif new_state == 'off':
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(new_state)
            self.adapter_props.Set(
                constants.ADAPTER_INTERFACE, 'Pairable', value)
            pairable = self.adapter_props.Get(
                constants.ADAPTER_INTERFACE, 'Pairable')
        return pairable

    def pairabletimeout(self, new_to=None):
        """Get or set the pairable timeout of the Adapter.

        :param new_to: (optional) new timeout value (UInt32).

        Whether changed or not, the pairable timeout is returned.
        """
        if new_to is None:
            pt = self.adapter_props.Get(constants.ADAPTER_INTERFACE,
                                        'PairableTimeout')
        else:
            timeout = dbus.UInt32(new_to)
            self.adapter_props.Set(constants.ADAPTER_INTERFACE,
                                   'PairableTimeout', timeout)
        return pt

    def discoverable(self, new_state=None):
        """Get or set the discoverable state of the Adapter.

        :param new_state: (optional) on or off changes the state.

        Whether changed or not, the discoverable state is returned.
        """
        if new_state is None:
            discoverable = self.adapter_props.Get(
                constants.ADAPTER_INTERFACE, 'Discoverable')
        else:
            if new_state == 'on':
                value = dbus.Boolean(1)
            elif new_state == 'off':
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(new_state)
            self.adapter_props.Set(constants.ADAPTER_INTERFACE,
                                   'Discoverable', value)
            discoverable = self.adapter_props.Get(
                constants.ADAPTER_INTERFACE, 'Discoverable')
        return discoverable

    def discoverabletimeout(self, new_dt=None):
        """Get or set the discoverable timeout of the Adapter.

        :param new_dt: (optional) new timeout value (UInt32).

        Whether changed or not, the discoverable timeout is returned.
        """
        if new_dt is None:
            dt = self.adapter_props.Get(constants.ADAPTER_INTERFACE,
                                        'DiscoverableTimeout')
        else:
            to = dbus.UInt32(new_dt)
            self.adapter_props.Set(constants.ADAPTER_INTERFACE,
                                   'DiscoverableTimeout', to)
            dt = self.adapter_props.Get(constants.ADAPTER_INTERFACE,
                                        'DiscoverableTimeout')
        return dt

    def discovering(self):
        """Return whether the adapter is discovering."""
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'Discovering')

    def _discovering_timeout(self):
        """Test to see if discovering should stop"""
        self._nearby_count += 1
        if self._nearby_count > self._nearby_timeout:
            self.stop_discovery()
            self.mainloop.quit()
        return True

    def nearby_discovery(self, timeout=10):
        """Start discovery of nearby Bluetooth devices."""
        self._nearby_timeout = timeout
        self._nearby_count = 0

        GLib.timeout_add(1000, self._discovering_timeout)
        self.adapter_methods.StartDiscovery()
        self.mainloop.run()

    def stop_discovery(self):
        """Stop scanning of nearby Bluetooth devices."""
        self.adapter_methods.StopDiscovery()
