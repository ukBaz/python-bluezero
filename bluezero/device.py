"""Class and methods that represent a remote Bluetooth Device.

Classes:

- Device -- Remote Bluetooth Device Class
"""
from __future__ import absolute_import, print_function, unicode_literals

import dbus
import dbus.mainloop.glib
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

from bluezero import constants


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


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
        self.mainloop = GObject.MainLoop()

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
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Name')

    @property
    def icon(self):
        """
        Proposed icon name.

        This is set according to the freedesktop.org icon naming specification.
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Icon')

    @property
    def bt_class(self):
        """The Bluetooth class of device of the remote device."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Class')

    @property
    def appearance(self):
        """External appearance of device, as found on GAP service."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Appearance')

    @property
    def uuids(self):
        """List of 128-bit UUIDs that represent available remote services."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'UUIDs')

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
    def adapter(self):
        """The object path of the adapter the device belongs to."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Adapter')

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
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Modalias')

    @property
    def RSSI(self):
        """
        Received Signal Strength Indicator of the remote device.

        (This is inquiry or advertising RSSI).
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'RSSI')

    @property
    def tx_power(self):
        """Advertised transmitted power level (inquiry or advertising)."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'TxPower')

    @property
    def manufacturer_data(self):
        """
        Manufacturer specific advertisement data.

        Keys are 16 bits Manufacturer ID followed by its byte array value.
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE,
            'ManufacturerData')

    @property
    def service_data(self):
        """
        Service advertisement data.

        Keys are the UUIDs in string format followed by its byte array value.
        """
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE,
            'ServiceData')

    @property
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
