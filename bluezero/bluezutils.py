"""Utility functions for python-bluezero."""

# D-Bus import
import dbus

# python-bluezero constants import
from bluezero import constants


def get_managed_objects():
    """Return the objects currently managed by the DBus Object Manager."""
    bus = dbus.SystemBus()
    manager = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'),
        constants.DBUS_OM_IFACE)
    return manager.GetManagedObjects()


def find_adapter(pattern=None):
    """Find a Bluetooth adapter from the DBus Object Manager.

    :param pattern: (optional) pattern to match when looking for a specific
                    adapter.

    ... seealso:: :func:`find_adapter_in_objects`
    """
    return find_adapter_in_objects(get_managed_objects(), pattern)


def find_adapter_in_objects(objects, pattern=None):
    """Find a Bluetooth adapter filtered by pattern in objects.

    :param objects: list of DBus managed objects from `get_managed_objects()`
    :param pattern: (optional) pattern to match when looking for a specific
                    adapter.

    ... seealso:: :func: `get_managed_objects()`
    """
    bus = dbus.SystemBus()
    for path, ifaces in objects.items():
        adapter = ifaces.get(constants.ADAPTER_INTERFACE)
        if adapter is None:
            continue
        if (not pattern or
                pattern == adapter['Address'] or
                path.endswith(pattern)):
            obj = bus.get_object(constants.BLUEZ_SERVICE_NAME, path)
            return dbus.Interface(obj, constants.ADAPTER_INTERFACE)
    raise Exception('No Bluetooth adapter found')


def find_device(device_address, adapter_pattern=None):
    """Find a device from the DBus Object Manager.

    :param device_address: device address that needs to be found
    :param pattern: (optional) pattern to match when looking for a specific
                    device.

    ... seealso:: :func:`find_device_in_objects`
    """
    return find_device_in_objects(
        get_managed_objects(),
        device_address,
        adapter_pattern)


def find_device_in_objects(objects, device_address, adapter_pattern=None):
    """Find a device in the managed DBus Objects.

    :param objects: list of DBus managed objects from `get_managed_objects()`
    :param device_address: device address that needs to be found
    :param pattern: (optional) pattern to match when looking for a specific
                    device.

    """
    bus = dbus.SystemBus()
    path_prefix = ''
    if adapter_pattern:
        adapter = find_adapter_in_objects(objects, adapter_pattern)
        path_prefix = adapter.object_path
    for path, ifaces in objects.items():
        device = ifaces.get(constants.DEVICE_INTERFACE)
        if device is None:
            continue
        if (device['Address'] == device_address and
                path.startswith(path_prefix)):
            obj = bus.get_object(constants.BLUEZ_SERVICE_NAME, path)
            return dbus.Interface(obj, constants.DEVICE_INTERFACE)

    raise Exception('Bluetooth device not found')

##########################
# GATT Interface functions
##########################


def get_gatt_manager_interface():
    """Return the DBus Interface for a Bluez GATT Manager."""
    return dbus.Interface(
        dbus.SystemBus().get_object(constants.BLUEZ_SERVICE_NAME,
                                    '/org/bluez/hci0'),
        constants.GATT_MANAGER_IFACE)


def get_gatt_service_interface():
    """Return the DBus Interface for a Bluez GATT Service."""
    return dbus.Interface(
        dbus.SystemBus().get_object(constants.BLUEZ_SERVICE_NAME,
                                    '/org/bluez/hci0'),
        constants.GATT_SERVICE_IFACE)


def get_gatt_characteristic_interface():
    """Return the DBus Interface for a Bluez GATT Characteristic."""
    return dbus.Interface(
        dbus.SystemBus().get_object(constants.BLUEZ_SERVICE_NAME,
                                    '/org/bluez/hci0'),
        constants.GATT_CHRC_IFACE)


def get_gatt_descriptor_interface():
    """Return the DBus Interface for a Bluez GATT Descriptor."""
    return dbus.Interface(
        dbus.SystemBus().get_object(constants.BLUEZ_SERVICE_NAME,
                                    '/org/bluez/hci0'),
        constants.GATT_DESC_IFACE)


def get_advert_manager_interface():
    """Return the DBus Interface for a Bluez GATT LE Advertising Manager."""
    return dbus.Interface(
        dbus.SystemBus().get_object(constants.BLUEZ_SERVICE_NAME,
                                    '/org/bluez/hci0'),
        constants.LE_ADVERTISING_MANAGER_IFACE)

#############################
# Interface search functions
#############################


def find_ad_adapter(bus):
    """Find the advertising manager interface.

    :param bus: D-Bus bus object that is searched.
    """
    remote_om = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'),
        constants.DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if constants.LE_ADVERTISING_MANAGER_IFACE in props:
            return o

    return None


def find_gatt_adapter(bus):
    """Find the GATT manager interface.

    :param bus: D-Bus bus object that is searched.
    """
    remote_om = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'),
        constants.DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if constants.GATT_MANAGER_IFACE in props:
            return o

    return None
