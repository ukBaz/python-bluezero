"""Class and methods that represent a remote Bluetooth Device.

Classes:

- Device -- Remote Bluetooth Device Class
"""
import dbus
import dbus.exceptions

from bluezero import constants
from bluezero import dbus_tools
import bluezero.adapter
from bluezero import tools


logger = tools.create_module_logger(__name__)


class Device:
    """Remote Bluetooth Device Class.

    This class instantiates an object that interacts with a remote
    Bluetooth device.
    """

    @staticmethod
    def available(adapter_address=None):
        """A generator yielding a Device object for every discovered device."""
        mng_objs = dbus_tools.get_managed_objects()
        adapters = {
            adapter.path: adapter.address
            for adapter in bluezero.adapter.Adapter.available()
        }
        for obj in mng_objs.values():
            device = obj.get(constants.DEVICE_INTERFACE, None)
            if device:
                adapter = adapters[device['Adapter']]
                if adapter_address is None or adapter == adapter_address:
                    yield Device(adapter, device['Address'])

    def __init__(self, adapter_addr, device_addr):
        """Default initialiser.

        Creates object for the specified remote Bluetooth device.
        This is on the specified adapter specified.

        :param adapter_addr: Address of the local Bluetooth adapter.
        :param device_addr: Address of the remote Bluetooth device.
        """
        self.bus = dbus.SystemBus()
        device_path = dbus_tools.get_dbus_path(adapter_addr, device_addr)
        if not device_path:
            raise ValueError("Cannot find a device: " + device_addr +
                             " using adapter: " + adapter_addr)

        self.remote_device_path = device_path
        self.remote_device_obj = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.remote_device_path)
        self.remote_device_methods = dbus.Interface(
            self.remote_device_obj,
            constants.DEVICE_INTERFACE)
        self.remote_device_props = dbus.Interface(self.remote_device_obj,
                                                  dbus.PROPERTIES_IFACE)

    @property
    def address(self):
        """Return the remote device address."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Address')

    @property
    def name(self):
        """Return the remote device name."""
        return dbus_tools.get(
            self.remote_device_props, constants.DEVICE_INTERFACE,
            'Name', None)

    @property
    def icon(self):
        """
        Proposed icon name.

        This is set according to the freedesktop.org icon naming specification.
        """
        return dbus_tools.get(
            self.remote_device_props, constants.DEVICE_INTERFACE, 'Icon', None)

    @property
    def bt_class(self):
        """The Bluetooth class of device of the remote device."""
        return dbus_tools.get(self.remote_device_props,
                              constants.DEVICE_INTERFACE,
                              'Class', None)

    @property
    def appearance(self):
        """External appearance of device, as found on GAP service."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Appearance')

    @property
    def uuids(self):
        """List of 128-bit UUIDs that represent available remote services."""
        return dbus_tools.get(self.remote_device_props,
                              constants.DEVICE_INTERFACE,
                              'UUIDs', None)

    @property
    def paired(self):
        """Indicate whether the remote device is paired."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Paired')

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Connected')

    @property
    def trusted(self):
        """Indicate whether the remote device is seen as trusted."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE,
            'Trusted')

    @trusted.setter
    def trusted(self, new_state):
        """Indicate whether the remote device is seen as trusted."""
        self.remote_device_props.Set(
            constants.DEVICE_INTERFACE,
            'Trusted',
            new_state)

    @property
    def blocked(self):
        """Indicate whether the remote device is seen as blocked."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE,
            'Blocked')

    @blocked.setter
    def blocked(self, new_state):
        """Indicate whether the remote device is seen as blocked."""
        self.remote_device_props.Set(
            constants.DEVICE_INTERFACE,
            'Blocked',
            new_state)

    @property
    def alias(self):
        """remote device alias"""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Alias')

    @alias.setter
    def alias(self, new_alias):
        """remote device alias."""
        self.remote_device_props.Set(
            constants.DEVICE_INTERFACE,
            'Alias',
            new_alias)

    @property
    def _adapter(self):
        """The D-Bus object path of the adapter the device belongs to."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Adapter')

    @property
    def adapter(self):
        """The address of the adapter the device belongs to."""
        adapter_obj = dbus_tools.get_dbus_obj(self._adapter)
        adapter_props = dbus_tools.get_dbus_iface(dbus.PROPERTIES_IFACE,
                                                  adapter_obj)
        return dbus_tools.get(adapter_props,  constants.ADAPTER_INTERFACE,
                              'Address')

    @property
    def legacy_pairing(self):
        """Indicate the legacy pairing status.

        Set to true if the device only supports the pre-2.1 pairing mechanism.
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE,
            'LegacyPairing')

    @legacy_pairing.setter
    def legacy_pairing(self, new_status):
        """Indicate the legacy pairing status.

        Set to true if the device only supports the pre-2.1 pairing mechanism.
        """
        self.remote_device_props.Set(
            constants.DEVICE_INTERFACE,
            'LegacyPairing',
            new_status)

    @property
    def modalias(self):
        """
        Remote Device ID information in modalias format.

        Used by the kernel and udev.
        """
        return dbus_tools.get(self.remote_device_props,
                              constants.DEVICE_INTERFACE,
                              'Modalias', None)

    @property
    def RSSI(self):  # pylint: disable=invalid-name
        """
        Received Signal Strength Indicator of the remote device.

        (This is inquiry or advertising RSSI).
        """
        return dbus_tools.get(self.remote_device_props,
                              constants.DEVICE_INTERFACE,
                              'RSSI', None)

    @property
    def tx_power(self):
        """Advertised transmitted power level (inquiry or advertising)."""
        return dbus_tools.get(self.remote_device_props,
                              constants.DEVICE_INTERFACE,
                              'TxPower', None)

    @property
    def manufacturer_data(self):
        """
        Manufacturer specific advertisement data.

        Keys are 16 bits Manufacturer ID followed by its byte array value.
        """
        return dbus_tools.get(self.remote_device_props,
                              constants.DEVICE_INTERFACE,
                              'ManufacturerData', None)

    @property
    def service_data(self):
        """
        Service advertisement data.

        Keys are the UUIDs in string format followed by its byte array value.
        """
        return dbus_tools.get(self.remote_device_props,
                              constants.DEVICE_INTERFACE,
                              'ServiceData', None)

    @property
    def services_resolved(self):
        """Indicate whether or not service discovery has been resolved."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE,
            'ServicesResolved')

    @property
    def services_available(self):
        """Get a list of Service UUIDs available on this device"""
        return dbus_tools.get_services(self.remote_device_obj.object_path)

    def pair(self):
        """
        Pair the device
        """
        self.remote_device_methods.Pair()

    def cancel_pairing(self):
        """
        This method can be used to cancel a pairing
        operation initiated by the pair method
        """
        self.remote_device_methods.CancelPairing()

    def connect(self, profile=None, timeout=35):
        """
        Initiate a connection to the remote device.

        :param profile: (optional) profile to use for the connection.
        :param timeout: (optional) the number of seconds to spend trying
               to connect.
        """
        try:
            if profile is None:
                self.bus.call_blocking(constants.BLUEZ_SERVICE_NAME,
                                       self.remote_device_path,
                                       constants.DEVICE_INTERFACE,
                                       'Connect', '', [], timeout=timeout)
            else:
                # need a device to test next line with.  for now, timeout
                # ignored for profile connections.
                # self.bus.call_blocking(constants.BLUEZ_SERVICE_NAME,
                # self.remote_device_path, constants.DEVICE_INTERFACE,
                # 'ConnectProfile', 's', [profile], timeout=timeout)
                self.remote_device_methods.ConnectProfile(profile)
        except dbus.exceptions.DBusException as dbus_exception:
            dbus_error_type = 'org.freedesktop.DBus.Error.NoReply'
            if dbus_exception.get_dbus_name() == dbus_error_type:
                # move driver back from connecting state to disconnected state
                self.disconnect()
            raise dbus_exception

    def disconnect(self):
        """Disconnect from the remote device."""
        self.remote_device_methods.Disconnect()
