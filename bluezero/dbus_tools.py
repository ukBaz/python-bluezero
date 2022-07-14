"""Utility functions for DBus use within Bluezero."""

# Standard libraries
import re
import subprocess

# D-Bus import
import dbus

# python-bluezero constants import
from bluezero import constants
from bluezero import tools

logger = tools.create_module_logger(__name__)


def bluez_version():
    """
    get the version of the BlueZ daemon being used on the system

    :return: String of BlueZ version
    """
    cmd = ['bluetoothctl', '-v']
    cmd_output = subprocess.run(cmd, capture_output=True, check=True)
    version = cmd_output.stdout.decode('utf-8').split()
    return version[1]


def bluez_experimental_mode():
    """
    Return True if the BlueZ daemon service is in experimental mode
    :return: True if experimental enabled
    """
    status = subprocess.check_output('service bluetooth status', shell=True)
    if re.search('--experimental', status.decode('utf-8')) is None:
        return False
    else:
        return True


def interfaces_added(path, interfaces):
    """
    Callback for when an interface is added

    :param path:
    :param interfaces:
    :return:
    """
    if constants.DEVICE_INTERFACE in interfaces:
        logger.debug('Device added at %s', path)


def properties_changed(interface, changed, invalidated, path):
    """
    Callback for when properties are changed

    :param interface:
    :param changed:
    :param invalidated:
    :param path:
    :return:
    """
    if constants.DEVICE_INTERFACE in interface:
        for prop in changed:
            logger.debug('%s:%s Property %s new value %s', interface, path,
                         prop, changed[prop])


def get_dbus_obj(dbus_path):
    """
    Get the the DBus object for the given path
    :param dbus_path:
    :return:
    """
    bus = dbus.SystemBus()
    return bus.get_object(constants.BLUEZ_SERVICE_NAME, dbus_path)


def get_dbus_iface(iface, dbus_obj):
    """
    Return the DBus interface object for given interface and DBus object
    :param iface:
    :param dbus_obj:
    :return:
    """
    return dbus.Interface(dbus_obj, iface)


def get_managed_objects():
    """Return the objects currently managed by the DBus Object Manager."""
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object(
        constants.BLUEZ_SERVICE_NAME, '/'),
        constants.DBUS_OM_IFACE)
    return manager.GetManagedObjects()


def get_mac_addr_from_dbus_path(path):
    """
    [Deprecated] Function to get the address of a remote device from
    a given D-Bus path. Path must include device part
    (e.g. dev_XX_XX_XX_XX_XX_XX)
    """
    logger.warning('get_mac_addr_from_dbus_path has been deprecated and has '
                   'been replaced with get_device_address_from_dbus_path')
    return get_device_address_from_dbus_path(path)


def get_device_address_from_dbus_path(path):
    """
    [Deprecated] Function to get the address of a remote device from
    a given D-Bus path. Path must include device part
    (e.g. dev_XX_XX_XX_XX_XX_XX)
    """
    for path_elem in path.split('/'):
        if path_elem.startswith('dev_'):
            return path_elem.replace("dev_", '').replace("_", ":")
    return ''


def get_adapter_address_from_dbus_path(path):
    """Return the address of the adapter from the a DBus path"""
    result = re.match(r'/org/bluez/hci\d+', path)
    mngd_objs = get_managed_objects()
    return mngd_objs[result.group(0)][constants.ADAPTER_INTERFACE]['Address']


def _get_dbus_path2(objects, parent_path, iface_in, prop, value):
    """
    Find DBus path for given DBus interface with property of a given value.

    :param objects: Dictionary of objects to search
    :param parent_path: Parent path to include in search
    :param iface_in: The interface of interest
    :param prop: The property to search for
    :param value: The value of the property being searched for
    :return: Path of object searched for
    """
    if parent_path is None:
        return None
    for path, iface in objects.items():
        props = iface.get(iface_in)
        if props is None:
            continue
        dev_name = "dev_" + value.lower().replace(":", "_")
        if (props[prop].lower() == value.lower() or
            path.lower().endswith(dev_name)) \
                and path.startswith(parent_path):
            return path
    return None


def get_dbus_path(adapter=None,
                  device=None,
                  service=None,
                  characteristic=None,
                  descriptor=None):
    """
    Return a DBus path for the given properties
    :param adapter: Adapter address
    :param device: Device address
    :param service: GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: DBus path
    """
    bus = dbus.SystemBus()
    manager = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'),
        constants.DBUS_OM_IFACE)
    mngd_objs = manager.GetManagedObjects()

    _dbus_obj_path = None

    if adapter is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         '/org/bluez',
                                         constants.ADAPTER_INTERFACE,
                                         'Address',
                                         adapter)

    if device is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.DEVICE_INTERFACE,
                                         'Address',
                                         device)

    if service is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_SERVICE_IFACE,
                                         'UUID',
                                         service)

    if characteristic is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_CHRC_IFACE,
                                         'UUID',
                                         characteristic)

    if descriptor is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_DESC_IFACE,
                                         'UUID',
                                         descriptor)
    return _dbus_obj_path


def get_profile_path(adapter,
                     device,
                     profile):
    """
    Return a DBus path for the given properties

    :param adapter: Adapter address
    :param device: Device address
    :param profile:
    :return:
    """
    bus = dbus.SystemBus()
    manager = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'),
        constants.DBUS_OM_IFACE)
    mngd_objs = manager.GetManagedObjects()

    _dbus_obj_path = None

    if adapter is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         '/org/bluez',
                                         constants.ADAPTER_INTERFACE,
                                         'Address',
                                         adapter)
    if device is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.DEVICE_INTERFACE,
                                         'Address',
                                         device)

    if profile is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_PROFILE_IFACE,
                                         'UUID',
                                         profile)
    return _dbus_obj_path


def get_iface(adapter=None,
              device=None,
              service=None,
              characteristic=None,
              descriptor=None):
    """
    For the given list of properties return the deepest interface

    :param adapter: Adapter address
    :param device: Device address
    :param service: GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: DBus Interface
    """
    if adapter is not None:
        _iface = constants.ADAPTER_INTERFACE

    if device is not None:
        _iface = constants.DEVICE_INTERFACE

    if service is not None:
        _iface = constants.GATT_SERVICE_IFACE

    if characteristic is not None:
        _iface = constants.GATT_CHRC_IFACE

    if descriptor is not None:
        _iface = constants.GATT_DESC_IFACE

    return _iface


def get_methods(adapter=None,
                device=None,
                service=None,
                characteristic=None,
                descriptor=None):
    """
    Get methods available for the specified

    :param adapter: Adapter Address
    :param device: Device Address
    :param service: GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: Object of the DBus methods available
    """
    path_obj = get_dbus_path(adapter,
                             device,
                             service,
                             characteristic,
                             descriptor)

    iface = get_iface(adapter,
                      device,
                      service,
                      characteristic,
                      descriptor)
    if path_obj is not None:
        return get_dbus_iface(iface, get_dbus_obj(path_obj))
    else:
        return None


def get_props(adapter=None,
              device=None,
              service=None,
              characteristic=None,
              descriptor=None):
    """
    Get properties for the specified object

    :param adapter: Adapter Address
    :param device:  Device Address
    :param service:  GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: Object of the DBus properties available
    """
    path_obj = get_dbus_path(adapter,
                             device,
                             service,
                             characteristic,
                             descriptor)
    if path_obj is not None:
        return get_dbus_iface(dbus.PROPERTIES_IFACE, get_dbus_obj(path_obj))
    else:
        return None


def get_services(path_obj):
    """
    Return a list of GATT Service UUIDs for a given Bluetooth device D-Bus path

    :param path_obj: D-Bus path for remote Bluetooth device
    :return: List of GATT Service UUIDs
    """
    found_services = []
    valid_structure = re.match(r'/org/bluez/hci\d+/dev(_([0-9A-Fa-f]){2}){6}',
                               path_obj)
    if not valid_structure:
        return found_services
    else:
        mngd_obj = get_managed_objects()
        for path in mngd_obj:
            if path.startswith(path_obj):
                srv_uuid = mngd_obj[path].get(
                    constants.GATT_SERVICE_IFACE, {}).get('UUID')
                if srv_uuid:
                    found_services.append(str(srv_uuid))
        return found_services


def get_device_addresses(name_contains):
    """
    Finds device whose name contains the string

    :param name_contains: String to be found in device name
    :return: List of dictionaries wth Device address and name
    """
    found = []
    mngd_obj = get_managed_objects()
    for path in mngd_obj:
        dev_name = mngd_obj[path].get(
            constants.DEVICE_INTERFACE, {}).get('Name')
        if dev_name and name_contains in dev_name:
            dev_addr = mngd_obj[path].get(
                constants.DEVICE_INTERFACE, {}).get('Address')
            found.append({dev_addr: dev_name})
    return found


def get(dbus_prop_obj, dbus_iface, prop_name, default=None):
    """
    Get a property from a D-Bus object and provide a default if the property
    does not exist. Similar to the "get" functionality on a python dictionary.

    :param dbus_prop_obj: The output object from dbus_tools.get_props
    :param dbus_iface: D-Bus Interface name e.g. 'org.bluez.Device1'
    :param prop_name: The name of the property
    :param default: What value to return if the property does not exist.
    :return: The property value if it exists or the default value
    """
    try:
        return dbus_prop_obj.Get(dbus_iface, prop_name)
    except dbus.exceptions.DBusException as dbus_exception:
        err_name = dbus_exception.get_dbus_name()
        err_msg = dbus_exception.get_dbus_message()
        if 'UnknownProperty' in err_name:
            return default
        elif 'no such property' in err_msg.casefold():
            return default
        else:
            raise dbus_exception


def str_to_dbusarray(word):
    """Helper function to represent Python string as D-Dbus Byte array"""
    return dbus.Array([dbus.Byte(ord(letter)) for letter in word], 'y')


def bytes_to_dbusarray(bytesarray):
    """Helper function to represent Python bytearray as D-Bus Byte array"""
    return dbus.Array([dbus.Byte(elem) for elem in bytesarray], 'y')


def dbus_to_python(data):
    """convert dbus data types to python native data types"""
    if isinstance(data, dbus.String):
        data = str(data)
    elif isinstance(data, dbus.Boolean):
        data = bool(data)
    elif isinstance(data, dbus.Byte):
        data = int(data)
    elif isinstance(data, dbus.UInt16):
        data = int(data)
    elif isinstance(data, dbus.UInt32):
        data = int(data)
    elif isinstance(data, dbus.Int64):
        data = int(data)
    elif isinstance(data, dbus.Double):
        data = float(data)
    elif isinstance(data, dbus.ObjectPath):
        data = str(data)
    elif isinstance(data, dbus.Array):
        if data.signature == dbus.Signature('y'):
            data = bytearray(data)
        else:
            data = [dbus_to_python(value) for value in data]
    elif isinstance(data, dbus.Dictionary):
        new_data = dict()
        for key in data:
            new_data[dbus_to_python(key)] = dbus_to_python(data[key])
        data = new_data
    return data
