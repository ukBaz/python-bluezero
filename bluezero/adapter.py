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
from bluezero import bluezutils
from bluezero import constants

# Main eventloop import
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

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
    >>> dongle = adapter.Adapter()
    >>> dongle.powered('on')

    """

    def __init__(self, dev_id=None):
        """Default initialiser.

        Creates the D-Bus interface to the specified device ID.  If no device
        ID is given, it will find the default device.

        :param dev_id: (optional) device ID to initialise with.
        """
        self.bus = dbus.SystemBus()
        self.dev_id = dev_id
        self.adapter_iface = bluezutils.find_adapter(dev_id)
        self.adapter_path = bluezutils.find_adapter(dev_id).object_path
        self.adapter = dbus.Interface(
            self.bus.get_object(
                'org.bluez',
                self.adapter_path),
            'org.freedesktop.DBus.Properties'
        )
        self.compact = True
        self.devices = {}

    def address(self):
        """Return the adapter MAC address."""
        return self.adapter.Get(constants.ADAPTER_INTERFACE, 'Address')

    def name(self):
        """Return the adapter name."""
        return self.adapter.Get(constants.ADAPTER_INTERFACE, 'Name')

    def alias(self, new_alias=None):
        """Return or set the adapter alias.

        :param new_alias: (optional) the new alias of the adapter.
        """
        if new_alias is None:
            return self.adapter.Get(constants.ADAPTER_INTERFACE, 'Alias')
        else:
            self.adapter.Set(constants.ADAPTER_INTERFACE, 'Alias', new_alias)

    def list(self):
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
            powered = self.adapter.Get(constants.ADAPTER_INTERFACE, 'Powered')
        else:
            if new_state == 'on':
                value = dbus.Boolean(1)
            elif new_state == 'off':
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(new_state)
            self.adapter.Set(constants.ADAPTER_INTERFACE, 'Powered', value)
            powered = self.adapter.Get(constants.ADAPTER_INTERFACE, 'Powered')
        return powered

    def pairable(self, new_state=None):
        """Get or set the pairable state of the Adapter.

        :param new_state: (optional) on or off changes the state.

        Whether changed or not, the pairable state is returned.
        """
        if new_state is None:
            pairable = self.adapter.Get(constants.ADAPTER_INTERFACE,
                                        'Pairable')
        else:
            if new_state == 'on':
                value = dbus.Boolean(1)
            elif new_state == 'off':
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(new_state)
            self.adapter.Set(constants.ADAPTER_INTERFACE, 'Pairable', value)
            pairable = self.adapter.Get(constants.ADAPTER_INTERFACE,
                                        'Pairable')
        return pairable

    def pairabletimeout(self, new_to=None):
        """Get or set the pairable timeout of the Adapter.

        :param new_to: (optional) new timeout value (UInt32).

        Whether changed or not, the pairable timeout is returned.
        """
        if new_to is None:
            pt = self.adapter.Get(constants.ADAPTER_INTERFACE,
                                  'PairableTimeout')
        else:
            timeout = dbus.UInt32(new_to)
            self.adapter.Set(constants.ADAPTER_INTERFACE,
                             'PairableTimeout', timeout)
        return pt

    def discoverable(self, new_state=None):
        """Get or set the discoverable state of the Adapter.

        :param new_state: (optional) on or off changes the state.

        Whether changed or not, the discoverable state is returned.
        """
        if new_state is None:
            discoverable = self.adapter.Get(constants.ADAPTER_INTERFACE,
                                            'Discoverable')
        else:
            if new_state == 'on':
                value = dbus.Boolean(1)
            elif new_state == 'off':
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(new_state)
            self.adapter.Set(constants.ADAPTER_INTERFACE,
                             'Discoverable', value)
            discoverable = self.adapter.Get(constants.ADAPTER_INTERFACE,
                                            'Discoverable')
        return discoverable

    def discoverabletimeout(self, new_dt=None):
        """Get or set the discoverable timeout of the Adapter.

        :param new_dt: (optional) new timeout value (UInt32).

        Whether changed or not, the discoverable timeout is returned.
        """
        if new_dt is None:
            dt = self.adapter.Get(constants.ADAPTER_INTERFACE,
                                  'DiscoverableTimeout')
        else:
            to = dbus.UInt32(new_dt)
            self.adapter.Set(constants.ADAPTER_INTERFACE,
                             'DiscoverableTimeout', to)
            dt = self.adapter.Get(constants.ADAPTER_INTERFACE,
                                  'DiscoverableTimeout')
        return dt

    def discovering(self):
        """Return whether the adapter is discovering."""
        return self.adapter.Get(constants.ADAPTER_INTERFACE, 'Discovering')

    @staticmethod
    def print_compact(address, properties):
        """Print a bluetooth adapter's properties using a compact notation.

        The notation is ``[logged] address name``.

        :param address: *ignored*
        :param properties: a dictionary of the bluetooth adapter's properties
        """
        name = ''
        address = '<unknown>'

        for key, value in properties.items():
            if type(value) is dbus.String:
                value = str(value).encode('ascii', 'replace')
            if key == 'Name':
                name = str(value)
            elif key == 'Address':
                address = str(value)

        if 'Logged' in properties:
            flag = '*'
        else:
            flag = ' '

        print('{0:s}{1:s} {2:s}'.format(flag, address, name))

        properties['Logged'] = True

    @staticmethod
    def print_normal(address, properties):
        """Print all of a bluetooth adapter's properties.

        :param address: address of the bluetooth adapter
        :param properties: a dictionary of the bluetooth adapter's properties
        """
        print('[ ' + address + ' ]')

        for key in properties.keys():
            value = properties[key]
            if type(value) is dbus.String:
                value = str(value).encode('ascii', 'replace')
            if key == 'Class':
                print('\t{0} = 0x{1:06x}'.format(key, value))
            else:
                print('\t{0} = {1}'.format(key, value))

        properties['Logged'] = True

    @staticmethod
    def skip_dev(old_dev, new_dev):
        """Determine whether to skip displaying a device.

        :param old_dev: dictionary of the registered devices.
        :param new_dev: properties of the new device.

        This function is used by the ``interfaces_added`` and
        ``properties_changed`` callbacks when scanning for devices.

        .. seealso:: :func:`interfaces_added`
        .. seealso:: :func:`properties_changed`
        """
        if 'Logged' not in old_dev:
            return False
        if 'Name' in old_dev:
            return True
        if 'Name' not in new_dev:
            return True
        return False

    def interfaces_added(self, path, interfaces):
        """Callback from a new interface when scanning for devices.

        :param path: hi path to the new device
        :param interfaces: dictionary of DBus interfaces.
        """
        # Select the Bluetooth Device interface
        properties = interfaces[constants.DEVICE_INTERFACE]
        if not properties:
            return

        if path in self.devices:
            dev = self.devices[path]

            if self.compact and self.skip_dev(dev, properties):
                return
            self.devices[path] = dict(list(self.devices[path].items()) +
                                      list(properties.items()))
        else:
            self.devices[path] = properties

        if 'Address' in self.devices[path]:
            address = properties['Address']
        else:
            address = '<unknown>'

        if self.compact:
            self.print_compact(address, self.devices[path])
        else:
            self.print_normal(address, self.devices[path])

    def properties_changed(self, interface, changed, invalidated, path):
        """Callback from properties changed when scanning for devices.

        :param interface: Object path to the interface that has changed.
        :param changed: dictionary of the changed properties.
        :param invalidated: *unused*
        :param path: hci path to the device that has changed.
        """
        # Ignore properties on anything but org.Bluez.Device1
        if interface != constants.DEVICE_INTERFACE:
            return

        if path in self.devices:
            dev = self.devices[path]

            if self.compact and self.skip_dev(dev, changed):
                return
            self.devices[path] = dict(list(self.devices[path].items()) +
                                      list(changed.items()))
        else:
            self.devices[path] = changed

        if 'Address' in self.devices[path]:
            address = self.devices[path]['Address']
        else:
            address = '<unknown>'

        if self.compact:
            self.print_compact(address, self.devices[path])
        else:
            self.print_normal(address, self.devices[path])

    def start_scan(self):
        """Start scanning for Bluetooth devices."""
        self.bus.add_signal_receiver(
            self.interfaces_added,
            dbus_interface=constants.DBUS_OM_IFACE,
            signal_name='InterfacesAdded')

        self.bus.add_signal_receiver(
            self.properties_changed,
            dbus_interface=constants.DBUS_PROP_IFACE,
            signal_name='PropertiesChanged',
            arg0=constants.DEVICE_INTERFACE,
            path_keyword='path')

        om = dbus.Interface(
            self.bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'),
            constants.DBUS_OM_IFACE)
        objects = om.GetManagedObjects()
        for path, interfaces in objects.items():
            if constants.DEVICE_INTERFACE in interfaces:
                self.devices[path] = interfaces[constants.DEVICE_INTERFACE]

        self.adapter_iface.StartDiscovery()

        mainloop = GObject.MainLoop()
        mainloop.run()

    def stop_scan(self):
        """Stop scanning for Bluetooth devices."""
        self.adapter_iface.StopDiscovery()
