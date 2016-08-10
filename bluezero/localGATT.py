"""Classes required to create a Bluetooth Peripheral.

Current classes include:
- Service -- Bluetooth Service
- Characteristic -- Bluetooth Characteristic
- Descriptor -- Bluetooth Descriptor
"""
from __future__ import absolute_import, print_function, unicode_literals

# D-Bus imports
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

# Main eventloop import
from gi.repository import GLib

# python-bluezero imports
from bluezero import constants

# Initialise the mainloop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


########################################
# Exception classes
#######################################
class InvalidArgsException(dbus.exceptions.DBusException):
    """This is a D-Bus exception class for Invalid Arguments.

    All this class does is set the internal variable ``_dbus_error_name`` to
    the object path for D-Bus Invalid Argument Exceptions.

    """

    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class Application(dbus.service.Object):
    """Bluez Application Class.

    This is the parent class for a python Bluez application.

    :Example:

    >>> app = localGATT.Application()
    >>> app.add_service(Service)
    >>> app.start()
    """
    def __init__(self, device_id=None):
        """Default initialiser.

        1. Initialises the program loop using ``GObject``.
        2. Registers the Application on the D-Bus.
        3. Initialises the list of services offered by the application.
        """
        # Initialise the D-Bus path and register it
        self.bus = dbus.SystemBus()
        self.path = '/ukBaz/bluezero'
        self.bus_name = dbus.service.BusName('ukBaz.bluezero', self.bus)
        dbus.service.Object.__init__(self, self.bus_name, self.path)

        # Objects to be associated with this service
        self.managed_objs = []

    @dbus.service.method(constants.DBUS_OM_IFACE,
                         out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        """Get all objects that are managed by the application.

        Return type is a dictionary whose keys are each registered object and
        values the properties of the given object.
        """
        response = {}

        for object in self.managed_objs:
            response[object.get_path()] = object.get_properties()

        return response

    def add_managed_object(self, object):
        """Add a service to the list of services offered by the Application.

        :param object: Python object of dbus path to be managed
        """
        self.managed_objs.append(object)

    def get_path(self):
        """Return the DBus object path"""
        return dbus.ObjectPath(self.path)


class Service(dbus.service.Object):
    """Bluez Service Class.

    This class represents a BLE Service.

    :Example:

    >>> your_service = localGATT.Service(UUID, primary)

    """

    PATH_BASE = '/ukBaz/bluezero/service'

    def __init__(self, service_id, uuid, primary):
        """Default initialiser.

        1. Registers the service on the D-Bus.
        2. Sets up the service UUID and primary flags.

        :param service_id:
        :param uuid: service BLE UUID
        :param primary: whether or not the service is a primary service
        """
        # Setup D-Bus object paths and register service
        self.path = self.PATH_BASE + str(service_id)
        self.bus = dbus.SystemBus()
        dbus.service.Object.__init__(self, self.bus, self.path)
        self.uuid = uuid
        self.primary = primary

    def get_path(self):
        """Return the DBus object path"""
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        """Return a dictionary of the service properties.

        The dictionary has the following keys:

        - UUID: the service UUID
        - Primary: whether the service is the primary service
        """
        return {
            constants.GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary
            }
        }

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        """Return the service properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface: interface to get the properties of.

        The interface must be ``org.bluez.GattService1`` otherwise an
        exception is raised.
        """
        if interface != constants.GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()
