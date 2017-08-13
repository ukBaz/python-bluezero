"""Utility functions for python-bluezero."""

# Standard libraries
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
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

# python-bluezero constants import
from bluezero import constants

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
mainloop = GObject.MainLoop()

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


def interfaces_added(path, interfaces):
    if constants.DEVICE_INTERFACE in interfaces:
        logger.debug('Device added at {}'.format(path))


def properties_changed(interface, changed, invalidated, path):
    if constants.DEVICE_INTERFACE in interface:
        for prop in changed:
            logger.debug(
                '{}:{} Property {} new value {}'.format(interface,
                                                        path,
                                                        prop,
                                                        changed[prop]))


def get_dbus_obj(dbus_path):
    bus = dbus.SystemBus()
    return bus.get_object(constants.BLUEZ_SERVICE_NAME, dbus_path)


def get_dbus_iface(iface, dbus_obj):
    return dbus.Interface(dbus_obj, iface)


def get_managed_objects():
    """Return the objects currently managed by the DBus Object Manager."""
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object(
        constants.BLUEZ_SERVICE_NAME, '/'),
        constants.DBUS_OM_IFACE)
    return manager.GetManagedObjects()


def _get_dbus_path2(objects, parent_path, iface_in, prop, value):
    if parent_path is None:
        raise ValueError('Bad combination of inputs: found nothing')
    for path, iface in objects.items():
        props = iface.get(iface_in)
        if props is None:
            continue
        if props[prop].lower() == value.lower() and \
                path.startswith(parent_path):
            return path


def get_dbus_path(adapter=None,
                  device=None,
                  service=None,
                  characteristic=None,
                  descriptor=None):
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

    path_obj = get_dbus_path(adapter,
                             device,
                             service,
                             characteristic,
                             descriptor)

    return get_dbus_iface(dbus.PROPERTIES_IFACE, path_obj)


#############################
# Interface search functions
#############################

def start_mainloop():
    mainloop.run()


def stop_mainloop():
    mainloop.quit()


def generic_error_cb(error):
    print('D-Bus call failed: ' + str(error))
    mainloop.quit()
