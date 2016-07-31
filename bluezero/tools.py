"""Utility functions for python-bluezero."""

# D-Bus import
import dbus
import dbus.mainloop.glib
from gi.repository import GLib

# python-bluezero constants import
from bluezero import constants

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
mainloop = GLib.MainLoop()
bus = dbus.SystemBus(mainloop)


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


def url_to_advert(url, frame_type, tx_power):
    """
    Encode as specified
    https://github.com/google/eddystone/blob/master/eddystone-url/README.md
    :param url:
    :return:
    """
    prefix_sel = None
    prefix_start = None
    prefix_end = None
    suffix_sel = None
    suffix_start = None
    suffix_end = None

    prefix = ('http://www.', 'https://www.', 'http://', 'https://')

    suffix = ('.com/', '.org/', '.edu/', '.net/', '.info/', '.biz/', '.gov/',
              '.com', '.org', '.edu', '.net', '.info', '.biz', '.gov'
              )
    encode_search = True

    for x in prefix:
        if x in url and encode_search is True:
            # print('match prefix ' + url)
            prefix_sel = prefix.index(x)
            prefix_start = url.index(prefix[prefix_sel])
            prefix_end = len(prefix[prefix_sel]) + prefix_start
            encode_search = False

    encode_search = True
    for y in suffix:
        if y in url and encode_search is True:
            # print('match suffix ' + y)
            suffix_sel = suffix.index(y)
            suffix_start = url.index(suffix[suffix_sel])
            suffix_end = len(suffix[suffix_sel]) + suffix_start
            encode_search = False

    service_data = [frame_type]
    service_data.extend([tx_power])
    if suffix_start is None:
        suffix_start = len(url)
        service_data.extend([prefix_sel])
        for x in range(prefix_end, suffix_start):
            service_data.extend([ord(url[x])])
    elif suffix_end == len(url):
        service_data.extend([prefix_sel])
        for x in range(prefix_end, suffix_start):
            service_data.extend([ord(url[x])])
        service_data.extend([suffix_sel])
    else:
        service_data.extend([prefix_sel])
        for x in range(prefix_end, suffix_start):
            service_data.extend([ord(url[x])])
        service_data.extend([suffix_sel])
        for x in range(suffix_end, len(url)):
            service_data.extend([ord(url[x])])

    return service_data


def start_mainloop():
    mainloop.run()


def stop_mainloop():
    mainloop.quit()
