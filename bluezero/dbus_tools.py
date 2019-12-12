"""Utility functions for DBus use within Bluezero."""

# Standard libraries
import re
import subprocess
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# D-Bus import
import dbus
import dbus.mainloop.glib

# python-bluezero constants import
from bluezero import constants

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


def bluez_version():
    """
    get the version of the BlueZ daemon being used on the system
    :return: String of BlueZ version
    """
    p = subprocess.Popen(['bluetoothctl', '-v'], stdout=subprocess.PIPE)
    ver = p.communicate()
    return str(ver[0].decode().rstrip())


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
        logger.debug('Device added at {}'.format(path))


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
            logger.debug(
                '{}:{} Property {} new value {}'.format(interface,
                                                        path,
                                                        prop,
                                                        changed[prop]))


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
    """Return the mac addres from a dev_XX_XX_XX_XX_XX_XX dbus path"""
    return path.split("/")[-1].replace("dev_", '').replace("_", ":")


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
        if props[prop].lower() == value.lower() and \
                path.startswith(parent_path):
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

    return get_dbus_iface(iface, get_dbus_obj(path_obj))


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

    return get_dbus_iface(dbus.PROPERTIES_IFACE, get_dbus_obj(path_obj))


def str_to_dbusarray(word):
    return dbus.Array([dbus.Byte(ord(letter)) for letter in word], 'y')


def bytes_to_dbusarray(bytesarray):
    return dbus.Array([dbus.Byte(elem) for elem in bytesarray], 'y')
