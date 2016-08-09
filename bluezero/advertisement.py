"""Class and methods that represent LE Advertising.

Classes:

- Advertisement -- Specifies the Advertisement Data to be broadcast
- AdvertisingManager -- register Advertisement Data which should be
  broadcast to devices
"""
from __future__ import absolute_import, print_function, unicode_literals

import dbus
import dbus.mainloop.glib
from gi.repository import GLib

from bluezero import constants


class Advertisement:
    """Advertisement data to broadcast Class."""

    def __init__(self, advertisement_path):
        """Default initialiser.

        Creates the D-Bus interface to the specified advertising data.
        The DBus path must be specified.

        :param device_path: DBus path to the advertising data.
        """
        self.bus = dbus.SystemBus()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = GLib.MainLoop()

        self.advertisement_path = advertisement_path
        self.advertisement_obj = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.advertisement_path)
        self.advertisement_methods = dbus.Interface(
            self.advertisement_obj,
            constants.LE_ADVERTISEMENT_IFACE)
        self.advertisement_props = dbus.Interface(self.advertisement_obj,
                                                  dbus.PROPERTIES_IFACE)

    def release(self):
        """
        This method gets called when the service daemon
        removes the Advertisement. A client can use it to do
        cleanup tasks. There is no need to call
        UnregisterAdvertisement because when this method gets
        called it has already been unregistered.
        :return:
        """
        self.advertisement_methods.Release()

    def type(self, advert_type=None):
        """Return or set the advertisement type.

        Possible values: "broadcast" or "peripheral"

        :param new_alias: (optional) type of advertisement requested.
        """
        if advert_type is None:
            return self.advertisement_props.Get(
                constants.LE_ADVERTISEMENT_IFACE, 'Type')
        else:
            self.advertisement_props.Set(constants.LE_ADVERTISEMENT_IFACE,
                                         'Alias',
                                         advert_type)

    def service_UUIDs(self, services_dict=None):
        """List of UUIDs to include in the "Service UUID" field of
            the Advertising Data.

        :param services_dict: list of service UUIDs
        :return:
        """
        if services_dict is None:
            return self.advertisement_props.Get(
                constants.LE_ADVERTISEMENT_IFACE, 'ServiceUUIDs')
        else:
            self.advertisement_props.Set(constants.LE_ADVERTISEMENT_IFACE,
                                         'ServiceUUIDs',
                                         services_dict)

    def manufacturer_data(self, manufact_data=None):
        """Dictionary of Manufacturer Data fields to include in
            the Advertising Data.  Keys are the Manufacturer ID
            to associate with the data

        :param manufact_data: Manufacturer Data dictionary
        :return:
        """
        if manufact_data is None:
            return self.advertisement_props.Get(
                constants.LE_ADVERTISEMENT_IFACE, 'ManufacturerData')
        else:
            self.advertisement_props.Set(constants.LE_ADVERTISEMENT_IFACE,
                                         'ManufacturerData',
                                         manufact_data)

    def solicit_UUIDs(self, solicit_data=None):
        """List of UUIDs to include in "Service Solicitation"
            Advertisement Data.

        :param solicit_data:
        :return:
        """
        if solicit_data is None:
            return self.advertisement_props.Get(
                constants.LE_ADVERTISEMENT_IFACE, 'SolicitUUIDs')
        else:
            self.advertisement_props.Set(constants.LE_ADVERTISEMENT_IFACE,
                                         'SolicitUUIDs',
                                         solicit_data)

    def service_data(self, service_content=None):
        """Dictionary of Service Data elements to include.
        The keys are the UUID to associate with the data

        :param service_content:
        :return:
        """
        if service_content is None:
            return self.advertisement_props.Get(
                constants.LE_ADVERTISEMENT_IFACE, 'ServiceData')
        else:
            self.advertisement_props.Set(constants.LE_ADVERTISEMENT_IFACE,
                                         'ServiceData',
                                         service_content)

    def include_tx_power(self, tx_include=None):
        """Boolean defining if Tx Power in the advertising packet.
            If missing, the Tx Power is not included.


        :param tx_include:
        :return:
        """
        if tx_include is None:
            return self.advertisement_props.Get(
                constants.LE_ADVERTISEMENT_IFACE, 'IncludeTxPower')
        else:
            self.advertisement_props.Set(constants.LE_ADVERTISEMENT_IFACE,
                                         'IncludeTxPower',
                                         tx_include)


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
            advertisement.advertisement_path,
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
            advertisement.advertisement_path
        )
