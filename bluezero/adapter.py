"""Class and methods that represent a Bluetooth Adapter."""

# D-Bus imports
import dbus
import dbus.mainloop.glib

# python-bluezero imports
from bluezero import constants
from bluezero import dbus_tools
from bluezero import async_tools
from bluezero import device
from bluezero import tools


logger = tools.create_module_logger(__name__)

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


class AdapterError(Exception):
    """Custom exception for missing Bluetooth adapter"""
    pass


def list_adapters():
    """Return list of adapters address available on system."""
    return [dongle.address for dongle in Adapter.available()]


class Adapter:
    """Bluetooth Adapter Class.

    This class instantiates an object that interacts with the physical
    Bluetooth device.

    :Example:

    >>> from bluezero import adapter
    >>> dongle = adapter.Adapter()
    >>> dongle.powered = True

    """

    @staticmethod
    def available():
        """
        A generator yielding an Adapter object for every attached adapter.
        """
        mng_objs = dbus_tools.get_managed_objects()
        found = False
        for obj in mng_objs.values():
            adapter = obj.get(constants.ADAPTER_INTERFACE, None)
            if adapter:
                found = True
                yield Adapter(adapter['Address'])
        if not found:
            raise AdapterError('No Bluetooth adapter found')

    def __init__(self, adapter_addr=None):
        """Default initialiser.

        Creates the interface to the local Bluetooth adapter device.
        If address is not given then first device is list is used.

        :param adapter_addr: Address of Bluetooth adapter to use.
        """
        self.bus = dbus.SystemBus()

        if adapter_addr is None:
            adapters = list_adapters()
            if len(adapters) > 0:
                adapter_addr = adapters[0]

        self.path = dbus_tools.get_dbus_path(adapter=adapter_addr)
        self.adapter_object = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.path)
        self.adapter_methods = dbus.Interface(self.adapter_object,
                                              constants.ADAPTER_INTERFACE)

        self.adapter_props = dbus.Interface(self.adapter_object,
                                            dbus.PROPERTIES_IFACE)

        self._nearby_timeout = 10
        self._nearby_count = 0
        self.mainloop = async_tools.EventLoop()

        self.on_disconnect = None
        self.on_connect = None
        self.on_device_found = None
        self.bus.add_signal_receiver(self._interfaces_added,
                                     dbus_interface=constants.DBUS_OM_IFACE,
                                     signal_name='InterfacesAdded')

        self.bus.add_signal_receiver(self._interfaces_removed,
                                     dbus_interface=constants.DBUS_OM_IFACE,
                                     signal_name='InterfacesRemoved')

        self.bus.add_signal_receiver(self._properties_changed,
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
    def alias(self):
        """Return the adapter alias.

        :param new_alias: the new alias of the adapter.
        """
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'Alias')

    @alias.setter
    def alias(self, new_alias):
        self.adapter_props.Set(
            constants.ADAPTER_INTERFACE, 'Alias', new_alias)

    def get_all(self):
        """Return dictionary of all the Adapter attributes."""
        return self.adapter_props.GetAll(constants.ADAPTER_INTERFACE)

    @property
    def powered(self):
        """power state of the Adapter.

        :param new_state: boolean.
        """
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'Powered')

    @powered.setter
    def powered(self, new_state):
        self.adapter_props.Set(
            constants.ADAPTER_INTERFACE, 'Powered', new_state)

    @property
    def pairable(self):
        """pairable state of the Adapter.

        :param new_state: boolean.
        """
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'Pairable')

    @pairable.setter
    def pairable(self, new_state):
        self.adapter_props.Set(
            constants.ADAPTER_INTERFACE, 'Pairable', new_state)

    @property
    def pairabletimeout(self):
        """The pairable timeout of the Adapter."""
        return self.adapter_props.Get(constants.ADAPTER_INTERFACE,
                                      'PairableTimeout')

    @pairabletimeout.setter
    def pairabletimeout(self, new_timeout):
        self.adapter_props.Set(constants.ADAPTER_INTERFACE,
                               'PairableTimeout', new_timeout)

    @property
    def discoverable(self):
        """Discoverable state of the Adapter."""
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'Discoverable')

    @discoverable.setter
    def discoverable(self, new_state):
        self.adapter_props.Set(constants.ADAPTER_INTERFACE,
                               'Discoverable', new_state)

    @property
    def discoverabletimeout(self):
        """Discoverable timeout of the Adapter."""
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

    @property
    def uuids(self):
        """List of 128-bit UUIDs that represent available remote services."""
        return self.adapter_props.Get(
            constants.ADAPTER_INTERFACE, 'UUIDs')

    def nearby_discovery(self, timeout=10):
        """Start discovery of nearby Bluetooth devices."""
        self._nearby_timeout = timeout
        self._nearby_count = 0

        # GLib.timeout_add(1000, self._discovering_timeout)
        async_tools.add_timer_ms(1000, self._discovering_timeout)
        self.adapter_methods.StartDiscovery()
        self.mainloop.run()

    def show_duplicates(self):
        """
        Show every advertisement from a device during
        Device Discovery if it contains ManufacturerData and/or
        ServiceData irrespective of whether they have been
        discovered previously
        """
        self.adapter_methods.SetDiscoveryFilter({'DuplicateData': True})

    def hide_duplicates(self):
        """
        Hide advertisements from a device during
        Device Discovery if it contains information already discovered
        """
        self.adapter_methods.SetDiscoveryFilter({'DuplicateData': False})

    def start_discovery(self):
        """
        Start discovery of nearby Bluetooth devices.

        :return: True on success otherwise False
        """
        self.adapter_methods.StartDiscovery()

    def stop_discovery(self):
        """Stop scanning of nearby Bluetooth devices."""
        self.adapter_methods.StopDiscovery()

    def remove_device(self, device_path):
        """Removes device at the given D-Bus path"""
        self.adapter_methods.RemoveDevice(device_path)

    def run(self):
        """Start the EventLoop for async operations"""
        self.mainloop.run()

    def quit(self):
        """Stop the EventLoop for async operations"""
        self.mainloop.quit()

    def _properties_changed(self, interface, changed, invalidated, path):
        """
        Handle DBus PropertiesChanged signal and
        call appropriate user callback
        """
        device_address = dbus_tools.get_device_address_from_dbus_path(path)
        adapter_addr = dbus_tools.get_adapter_address_from_dbus_path(path)
        if 'Connected' in changed:
            if all((changed['Connected'],
                    self.address == adapter_addr,
                    self.on_connect)):
                if tools.get_fn_parameters(self.on_connect) == 0:
                    self.on_connect()
                elif tools.get_fn_parameters(self.on_connect) == 1:
                    new_dev = device.Device(
                        adapter_addr=self.address,
                        device_addr=device_address)
                    self.on_connect(new_dev)
                elif tools.get_fn_parameters(self.on_connect) == 2:
                    self.on_connect(adapter_addr, device_address)
            elif not changed['Connected'] and self.on_disconnect:
                if tools.get_fn_parameters(self.on_disconnect) == 0:
                    logger.warning("using deprecated version of disconnect "
                                   "callback, move to on_disconnect(dev) "
                                   "with device parameter")
                    self.on_disconnect()
                elif tools.get_fn_parameters(self.on_disconnect) == 1:
                    new_dev = device.Device(
                        adapter_addr=self.address,
                        device_addr=device_address)
                    self.on_disconnect(new_dev)
                elif tools.get_fn_parameters(self.on_disconnect) == 2:
                    self.on_disconnect(self.address, device_address)

    def _interfaces_added(self, path, device_info):
        """
        Handle DBus InterfacesAdded signal and
        call appropriate user callback
        """
        dev_iface = constants.DEVICE_INTERFACE
        if constants.DEVICE_INTERFACE in device_info:
            dev_addr = device_info[dev_iface].get('Address')
            dev_connected = device_info[dev_iface].get('Connected')
            if self.on_device_found and dev_addr:
                new_dev = device.Device(
                    adapter_addr=self.address,
                    device_addr=dev_addr)
                self.on_device_found(new_dev)
            if all((self.on_connect, dev_connected, dev_addr)):
                new_dev = device.Device(
                    adapter_addr=self.address,
                    device_addr=dev_addr)
                self.on_connect(new_dev)

    def _interfaces_removed(self, path, device_info):
        """
        Handle DBus InterfacesRemoved signal and
        call appropriate user callback
        """
