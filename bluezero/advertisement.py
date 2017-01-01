"""Class and methods that represent LE Advertising.

Classes:

- Advertisement -- Specifies the Advertisement Data to be broadcast
- AdvertisingManager -- register Advertisement Data which should be
  broadcast to devices
"""
from __future__ import absolute_import, print_function, unicode_literals

import dbus
import dbus.exceptions
import dbus.service
import dbus.mainloop.glib
try:
    from gi.repository import GObject
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

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
mainloop = GObject.MainLoop()

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


########################################
# Exception classes
#######################################
class InvalidArgsException(dbus.exceptions.DBusException):
    """This is a D-Bus exception class for Invalid Arguments.

    All this class does is set the internal variable ``_dbus_error_name`` to
    the object path for D-Bus Invalid Argument Exceptions.

    """

    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class Advertisement(dbus.service.Object):
    """Advertisement data to broadcast Class.

    An example of an Eddystone beacon:
    :Example:

    >>> from bluezero import tools
    >>> from bluezero import advertisement
    >>> beacon = advertisement.Advertisement(1, 'broadcast')
    >>> beacon.service_UUIDs = ['FEAA']
    >>> beacon.service_data =  {'FEAA': [0x10, 0x00, 0x00, 0x63, 0x73,
    >>>                                  0x72, 0x00, 0x61, 0x62, 0x6f,
    >>>                                  0x75, 0x74]}
    >>> ad_manager = advertisement.AdvertisingManager('/org/bluez/hci0')
    >>> ad_manager.register_advertisement(beacon, {})
    >>> tools.start_mainloop()

    """

    def __init__(self, advert_id, ad_type):
        """Default initialiser.

        Creates the D-Bus interface to the specified advertising data.
        The DBus path must be specified.

        :param device_path: DBus path to the advertising data.
        """
        # Setup D-Bus object paths and register service
        self.path = '/ukBaz/bluezero/advertisement{0:04d}'.format(advert_id)
        self.bus = dbus.SystemBus()
        self.interface = constants.LE_ADVERTISEMENT_IFACE
        dbus.service.Object.__init__(self, self.bus, self.path)
        self.props = {
            constants.LE_ADVERTISEMENT_IFACE: {
                'Type': ad_type,
                'ServiceUUIDs': None,
                'ManufacturerData': None,
                'SolicitUUIDs': None,
                'ServiceData': None,
                'IncludeTxPower': False
            }
        }

    def get_path(self):
        """Return the DBus object path"""
        return dbus.ObjectPath(self.path)

    @dbus.service.method(constants.LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        """
        This method gets called when the service daemon
        removes the Advertisement. A client can use it to do
        cleanup tasks. There is no need to call
        UnregisterAdvertisement because when this method gets
        called it has already been unregistered.
        :return:
        """
        pass

    @property
    def service_UUIDs(self):
        """List of UUIDs that represent available services."""
        return self.Get(constants.LE_ADVERTISEMENT_IFACE,
                        'ServiceUUIDs')

    @service_UUIDs.setter
    def service_UUIDs(self, UUID):
        self.Set(constants.LE_ADVERTISEMENT_IFACE,
                 'ServiceUUIDs',
                 UUID)

    def manufacturer_data(self):
        """Manufacturer Data to be broadcast (Currently not supported)"""
        pass

    def solicit_UUIDs(self):
        """Manufacturer Data to be broadcast (Currently not supported)"""
        pass

    @property
    def service_data(self):
        """Service Data to be broadcast"""
        return self.Get(constants.LE_ADVERTISEMENT_IFACE,
                        'ServiceData')

    @service_data.setter
    def service_data(self, data):
        for UUID in data:
            self.Set(constants.LE_ADVERTISEMENT_IFACE,
                     'ServiceData',
                     {UUID: dbus.Array(data[UUID], signature='y')})

    @property
    def include_tx_power(self):
        """Include TX power in advert (Different from beacon packet)"""
        return self.Get(constants.LE_ADVERTISEMENT_IFACE,
                        'IncludeTxPower')

    @include_tx_power.setter
    def include_tx_power(self, state):
        return self.Set(constants.LE_ADVERTISEMENT_IFACE,
                        'IncludeTxPower', state)

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface_name):
        """Return the advertisement properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface: interface to get the properties of.

        The interface must be ``org.bluez.LEAdvertisement1`` otherwise an
        exception is raised.
        """
        if interface_name != constants.LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()

        response = {}
        response['Type'] = self.props[interface_name]['Type']
        if self.props[interface_name]['ServiceUUIDs'] is not None:
            response['ServiceUUIDs'] = dbus.Array(
                self.props[interface_name]['ServiceUUIDs'],
                signature='s')
        if self.props[interface_name]['ServiceData'] is not None:
            response['ServiceData'] = dbus.Dictionary(
                self.props[interface_name]['ServiceData'],
                signature='sv')
        if self.props[interface_name]['ManufacturerData'] is not None:
            response['ManufacturerData'] = dbus.Dictionary(
                self.props[interface_name]['ManufacturerData'],
                signature='qv')
        if self.props[interface_name]['SolicitUUIDs'] is not None:
            response['SolicitUUIDs'] = dbus.Array(
                self.props[interface_name]['SolicitUUIDs'],
                signature='s')
        response['IncludeTxPower'] = dbus.Boolean(
            self.props[interface_name]['IncludeTxPower'])

        return response

    @dbus.service.method(dbus.PROPERTIES_IFACE,
                         in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        """DBus API for getting a property value"""

        if interface_name != constants.LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()

        try:
            return self.GetAll(interface_name)[property_name]
        except KeyError:
            raise dbus.exceptions.DBusException(
                'no such property ' + property_name,
                name=interface_name + '.UnknownProperty')

    @dbus.service.method(dbus.PROPERTIES_IFACE,
                         in_signature='ssv', out_signature='')
    def Set(self, interface_name, property_name, value, *args, **kwargs):
        """Standard D-Bus API for setting a property value"""

        try:
            iface_props = self.props[interface_name]
        except KeyError:
            raise dbus.exceptions.DBusException(
                'no such interface ' + interface_name,
                name=self.interface + '.UnknownInterface')

        if property_name not in iface_props:
            raise dbus.exceptions.DBusException(
                'no such property ' + property_name,
                name=self.interface + '.UnknownProperty')

        iface_props[property_name] = value


def register_ad_cb():
    """Advertisement registration callback."""
    print('Advertisement registered')


def register_ad_error_cb(error):
    """Advertisement registration error callback."""
    print('Failed to register advertisement: ' + str(error))


class AdvertisingManager:
    def __init__(self, advert_mngr_path):
        self.bus = dbus.SystemBus()

        self.advert_mngr_path = advert_mngr_path
        self.advert_mngr_obj = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.advert_mngr_path)
        self.advert_mngr_methods = dbus.Interface(
            self.advert_mngr_obj,
            constants.LE_ADVERTISING_MANAGER_IFACE)
        self.advert_mngr_props = dbus.Interface(self.advert_mngr_obj,
                                                dbus.PROPERTIES_IFACE)

    def register_advertisement(self, advertisement, options=dbus.Array()):
        """
        Registers an advertisement object to be sent over the LE
        Advertising channel
        :param advertisement: Advertisement object
        :param options:
        :return:
        """
        self.advert_mngr_methods.RegisterAdvertisement(
            advertisement.path,
            options,
            reply_handler=register_ad_cb,
            error_handler=register_ad_error_cb
        )

    def unregister_advertisement(self, advertisement):
        """This unregisters the services that has been
            previously registered. The advertisement object
            must match the  value that was used
            on registration

        :param advertisement:
        :return:
        """
        self.advert_mngr_methods.UnregisterAdvertisement(
            advertisement.path
        )
