"""Class and methods that represent a remote Bluetooth Device.

Classes:

- Device -- Remote Bluetooth Device Class
"""
from __future__ import absolute_import, print_function, unicode_literals

import dbus
import dbus.mainloop.glib
from gi.repository import GLib

from bluezero import constants


class Device:
    """Remote Bluetooth Device Class.

    This class instantiates an object that interacts with a remote
    Bluetooth device via the D-Bus.
    """

    def __init__(self, device_path):
        """Default initialiser.

        Creates the D-Bus interface to the specified remote Bluetooth device.
        The DBus path must be specified.

        :param device_path: DBus path to the remote Bluetooth device.
        """
        self.bus = dbus.SystemBus()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = GLib.MainLoop()

        self.remote_device_path = device_path
        self.remote_device_obj = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.remote_device_path)
        self.remote_device_methods = dbus.Interface(
            self.remote_device_obj,
            constants.ADAPTER_INTERFACE)
        self.remote_device_props = dbus.Interface(self.remote_device_obj,
                                                  dbus.PROPERTIES_IFACE)

    def address(self):
        """Return the remote device address."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Address')

    def name(self):
        """Return the remote device name."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Name')

    def icon(self):
        """
        Proposed icon name.

        This is set according to the freedesktop.org icon naming specification.
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Icon')

    def bt_class(self):
        """The Bluetooth class of device of the remote device."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Class')

    def appearance(self):
        """External appearance of device, as found on GAP service."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Appearance')

    def uuids(self):
        """List of 128-bit UUIDs that represent available remote services."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'UUIDs')

    def paired(self):
        """Indicate whether the remote device is paired."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Paired')

    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Connected')

    def trusted(self, new_state=None):
        """
        Indicate whether the remote device is seen as trusted.

        This setting can be changed.

        :param new_state: (optional) True or False changes the state.

        Whether changed or not, the Trusted state is returned.
        """
        if new_state is None:
            trusted = self.remote_device_props.Get(
                constants.DEVICE_INTERFACE,
                'Trusted')
        else:
            if new_state:
                value = dbus.Boolean(1)
            elif not new_state:
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(new_state)
            self.remote_device.Set(
                constants.DEVICE_INTERFACE,
                'Trusted',
                value)
            trusted = self.remote_device_props.Get(
                constants.DEVICE_INTERFACE,
                'Trusted')
        return trusted

    def blocked(self, new_state=None):
        """
        Indicate whether the remote device is seen as blocked.

        This setting can be changed.

        :param new_state: (optional) True or False changes the state.

        Whether changed or not, the Blocked state is returned.
        """
        if new_state is None:
            blocked = self.remote_device_props.Get(
                constants.DEVICE_INTERFACE,
                'Blocked')
        else:
            if new_state:
                value = dbus.Boolean(1)
            elif not new_state:
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(new_state)
            self.remote_device.Set(
                constants.DEVICE_INTERFACE,
                'Blocked',
                value)
            blocked = self.remote_device_props.Get(
                constants.DEVICE_INTERFACE,
                'Blocked')
        return blocked

    def alias(self, new_alias=None):
        """Return or set the remote device alias.

        :param new_alias: (optional) the new alias of the remote device.
        """
        if new_alias is None:
            return self.remote_device_props.Get(
                constants.DEVICE_INTERFACE, 'Alias')
        else:
            self.remote_device.Set(
                constants.DEVICE_INTERFACE,
                'Alias',
                new_alias)

    def adapter(self):
        """The object path of the adapter the device belongs to."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Adapter')

    def legacy_pairing(self):
        """
        Indicate the legacy pairing status.

        Set to true if the device only supports the pre-2.1 pairing mechanism.
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE,
            'LegacyPairing')

    def modalias(self):
        """
        Remote Device ID information in modalias format.

        Used by the kernel and udev.
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Modalias')

    def RSSI(self):
        """
        Received Signal Strength Indicator of the remote device.

        (This is inquiry or advertising RSSI).
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'RSSI')

    def tx_power(self):
        """Advertised transmitted power level (inquiry or advertising)."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'TxPower')

    def manufacturer_data(self):
        """
        Manufacturer specific advertisement data.

        Keys are 16 bits Manufacturer ID followed by its byte array value.
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE,
            'ManufacturerData')

    def service_data(self):
        """
        Service advertisement data.

        Keys are the UUIDs in string format followed by its byte array value.
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE,
            'ServiceData')

    def services_resolved(self):
        """Indicate whether or not service discovery has been resolved."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE,
            'ServicesResolved')

    def connect(self, address=None, profile=None):
        """
        Initiate a connection to the remote device.

        :param address: unused
        :param profile: (optional) profile to use for the connection.
        """
        if profile is None:
            self.remote_device_methods.Connect()
        else:
            self.remote_device_methods.ConnectProfile(profile)

    def disconnect(self):
        """Disconnect from the remote device."""
        self.remote_device_methods.Disconnect()
