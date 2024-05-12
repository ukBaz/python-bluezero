"""
Class and methods that represent LE Advertising.
This class requires BlueZ to have the experimental flag enabled

Classes:

- Advertisement -- Specifies the Advertisement Data to be broadcast
- AdvertisingManager -- register Advertisement Data which should be
  broadcast to devices
"""
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

from bluezero import constants
from bluezero import dbus_tools
from bluezero import async_tools
from bluezero import adapter
from bluezero import tools

logger = tools.create_module_logger(__name__)

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


class Advertisement(dbus.service.Object):
    """Advertisement data to broadcast Class.

    An example of an Eddystone beacon:
    :Example:

    >>> from bluezero import advertisement
    >>> beacon = advertisement.Advertisement(1, 'broadcast')
    >>> beacon.service_UUIDs = ['FEAA']
    >>> beacon.service_data =  {'FEAA': [0x10, 0x08, 0x03, 0x75, 0x6B,
    >>>                                  0x42, 0x61, 0x7A, 0x2e, 0x67,
    >>>                                  0x69, 0x74, 0x68, 0x75, 0x62,
    >>>                                  0x2E, 0x69, 0x6F]}
    >>> ad_manager = advertisement.AdvertisingManager()
    >>> ad_manager.register_advertisement(beacon, {})
    >>> beacon.start()

    """

    def __init__(self, advert_id, ad_type):
        """Default initialiser.

        Creates the interface to the specified advertising data.
        The DBus path must be specified.

        :param advert_id: Unique ID of advertisement.
        :param ad_type: Possible values: "broadcast" or "peripheral"
        """
        # Setup D-Bus object paths and register service
        self.path = '/ukBaz/bluezero/advertisement{0:04d}'.format(advert_id)
        self.bus = dbus.SystemBus()
        self.mainloop = async_tools.EventLoop()
        self.interface = constants.LE_ADVERTISEMENT_IFACE
        dbus.service.Object.__init__(self, self.bus, self.path)
        self.props = {
            constants.LE_ADVERTISEMENT_IFACE: {
                'Type': ad_type,
                'ServiceUUIDs': None,
                'ManufacturerData': None,
                'SolicitUUIDs': None,
                'ServiceData': None,
                'Includes': set(),
                'Appearance': None,
                'LocalName': None
            }
        }

    def start(self):
        """Start GLib event loop"""
        self.mainloop.run()

    def stop(self):
        """Stop GLib event loop"""
        self.mainloop.quit()

    def get_path(self):
        """Return the DBus object path"""
        return dbus.ObjectPath(self.path)

    @dbus.service.method(constants.LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):  # pylint: disable=invalid-name
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
    def service_UUIDs(self):  # pylint: disable=invalid-name
        """List of UUIDs that represent available services."""
        return self.Get(constants.LE_ADVERTISEMENT_IFACE,
                        'ServiceUUIDs')

    @service_UUIDs.setter
    def service_UUIDs(self, UUID):  # pylint: disable=invalid-name
        self.Set(constants.LE_ADVERTISEMENT_IFACE,
                 'ServiceUUIDs',
                 UUID)

    def manufacturer_data(self, company_id, data):
        """Manufacturer Data to be broadcast"""
        return self.Set(constants.LE_ADVERTISEMENT_IFACE,
                        'ManufacturerData',
                        {company_id: dbus.Array(data, signature='y')})

    def solicit_UUIDs(self):  # pylint: disable=invalid-name
        """Manufacturer Data to be broadcast (Currently not supported)"""
        pass

    @property
    def service_data(self):
        """Service Data to be broadcast"""
        return self.Get(constants.LE_ADVERTISEMENT_IFACE,
                        'ServiceData')

    @service_data.setter
    def service_data(self, data):
        for uuid in data:
            self.Set(constants.LE_ADVERTISEMENT_IFACE,
                     'ServiceData',
                     {uuid: dbus.Array(data[uuid], signature='y')})

    @property
    def include_tx_power(self):
        """Include TX power in advert (Different from beacon packet)"""
        includes = self.Get(constants.LE_ADVERTISEMENT_IFACE, 'Includes')
        return 'tx-power' in includes

    @include_tx_power.setter
    def include_tx_power(self, state):
        if state:
            self.props[
                constants.LE_ADVERTISEMENT_IFACE][
                'Includes'].add('tx-power')
        else:
            self.props[
                constants.LE_ADVERTISEMENT_IFACE][
                'Includes'].discard('tx-power')

    @property
    def local_name(self):
        """Local name of the device included in Advertisement."""
        return self.Get(constants.LE_ADVERTISEMENT_IFACE, 'LocalName')

    @local_name.setter
    def local_name(self, name):
        self.Set(constants.LE_ADVERTISEMENT_IFACE, 'LocalName', name)

    @property
    def appearance(self):
        """Appearance to be used in the advertising report."""
        return self.Get(constants.LE_ADVERTISEMENT_IFACE, 'Appearance')

    @appearance.setter
    def appearance(self, appearance):
        self.Set(constants.LE_ADVERTISEMENT_IFACE, 'Appearance', appearance)

    @dbus.service.method(constants.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface_name):  # pylint: disable=invalid-name
        """Return the advertisement properties.

        This method is registered with the D-Bus at
        ``org.freedesktop.DBus.Properties``

        :param interface: interface to get the properties of.

        The interface must be ``org.bluez.LEAdvertisement1`` otherwise an
        exception is raised.
        """
        if interface_name != constants.LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()

        response = dict()
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
        if self.props[interface_name]['LocalName'] is not None:
            response['LocalName'] = dbus.String(
                    self.props[interface_name]['LocalName'])
        if self.props[interface_name]['Appearance'] is not None:
            response['Appearance'] = dbus.UInt16(
                    self.props[interface_name]['Appearance'])
        response['Includes'] = dbus.Array(
            self.props[interface_name]['Includes'], signature='s')

        return response

    @dbus.service.method(dbus.PROPERTIES_IFACE,
                         in_signature='ss', out_signature='v')
    def Get(self, interface_name,  # pylint: disable=invalid-name
            property_name):
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
    def Set(self,  # pylint: disable=invalid-name
            interface_name, property_name, value):
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
    """
    Associate the advertisement to an adapter.
    If no adapter specified then first adapter in list is used
    """

    def __init__(self, adapter_addr=None):

        self.bus = dbus.SystemBus()

        if adapter_addr is None:
            adapters = list(adapter.Adapter.available())
            if len(adapters) > 0:
                use_adapter = adapters[0]
                adapter_addr = use_adapter.address
        else:
            use_adapter = adapter.Adapter(adapter_addr)

        if not use_adapter.discoverable:
            use_adapter.discoverable = True
        self.advert_mngr_path = dbus_tools.get_dbus_path(adapter=adapter_addr)
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
            dbus.Dictionary(options, signature='sv'),
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
