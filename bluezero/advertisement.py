"""
Class and methods that represent LE Advertising.
This class requires BlueZ to have the experimental flag enabled

Classes:

- Advertisement -- Specifies the Advertisement Data to be broadcast
- AdvertisingManager -- register Advertisement Data which should be
  broadcast to devices
"""
import threading
from typing import List, Dict, Union

from gi.repository import GLib, Gio
import pkgutil

from bluezero import constants
from bluezero import async_tools
from bluezero import adapter
from bluezero import gio_dbus
from bluezero import tools

logger = tools.create_module_logger(__name__)


########################################
# Exception classes
#######################################
# class InvalidArgsException(dbus.exceptions.DBusException):
#     """This is a D-Bus exception class for Invalid Arguments.
#
#     All this class does is set the internal variable ``_dbus_error_name`` to
#     the object path for D-Bus Invalid Argument Exceptions.
#
#     """
#
#     _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class Advertisement(gio_dbus.DbusService):
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
        # Setup D-Bus object paths
        self.path = '/ukBaz/bluezero/advertisement{0:04d}'.format(advert_id)
        # Get introspection XML
        introspection_xml = pkgutil.get_data(
            'bluezero', "iface_xml/LEAdvertisement1.xml").decode()
        super().__init__(introspection_xml=introspection_xml,
                         publish_path=self.path)

        self.Type = ad_type
        self.ServiceUUIDs = []
        self.ManufacturerData = {}
        self.SolicitUUIDs = []
        self.ServiceData = {}
        self.Includes = []
        # LocalName = GLib.Variant('s', '')
        self.LocalName = None
        # Appearance = GLib.Variant.new_uint16(0)
        self.Appearance = None
        # Duration = GLib.Variant.new_uint16(0)
        self.Duration = None
        # Timeout = GLib.Variant.new_uint16(0)
        self.Timeout = None

        self.mainloop = async_tools.EventLoop()
        self._ad_thread = None

    def start(self):
        """Start GLib event loop"""
        self._ad_thread = threading.Thread(target=self.mainloop.run)
        self._ad_thread.daemon = False
        self._ad_thread.start()

    def stop(self):
        """Stop GLib event loop"""
        self.mainloop.quit()

    def get_path(self):
        """Return the DBus object path"""
        return GLib.Variant.new_path_object(self.path)

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
        return self.ServiceUUIDs.unpack()

    @service_UUIDs.setter
    def service_UUIDs(self, UUID):  # pylint: disable=invalid-name
        self.ServiceUUIDs = GLib.Variant('as', UUID)

    @property
    def manufacturer_data(self, company_id, data):
        """Manufacturer Data to be broadcast"""
        return self.ManufacturerData.unpack()

    @manufacturer_data.setter
    def manufacturer_data(self, manufacturer_data: Dict[int, List[int]]) -> None:
        """Manufacturer Data to be broadcast"""
        m_data = GLib.VariantBuilder(GLib.VariantType.new('a{qv}'))
        for key, value in manufacturer_data.items():
            g_key = GLib.Variant.new_uint16(key)
            g_value = GLib.Variant('ay', value)
            g_var = GLib.Variant.new_variant(g_value)
            g_dict = GLib.Variant.new_dict_entry(g_key, g_var)
            m_data.add_value(g_dict)
        self.ManufacturerData = m_data.end()

    @property
    def solicit_UUIDs(self):  # pylint: disable=invalid-name
        """UUIDs to include in "Service Solicitation" Advertisement Data"""
        return self.SolicitUUIDs.unpack()

    @solicit_UUIDs.setter
    def solicit_UUIDs(self, data: List[str]) -> None:
        self.SolicitUUIDs = GLib.Variant('as', data)

    @property
    def service_data(self):
        """Service Data to be broadcast"""
        return self.ServiceData.unpack()

    @service_data.setter
    def service_data(self, service_data):
        s_data = {}
        for key, value in service_data.items():
            gvalue = GLib.Variant('ay', value)
            s_data[key] = gvalue
        self.ServiceData = s_data

    @property
    def local_name(self) -> Union[str, None]:
        """Local name of the device included in Advertisement."""
        if self.LocalName:
            return self.LocalName.unpack()
        return None

    @local_name.setter
    def local_name(self, name: Union[str, None]):
        if name:
            self.LocalName = GLib.Variant.new_string(name)
        else:
            self.LocalName = None

    @property
    def appearance(self) -> int:
        """Appearance to be used in the advertising report."""
        return self.Appearance

    @appearance.setter
    def appearance(self, appearance: int) -> None:
        if appearance:
            self.Appearance = GLib.Variant.new_uint16(appearance)
        self.Appearance = None


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
    def __new__(cls, adapter_addr=None, *args, **kwargs):
        # We always want to get the same Proxy instance of the
        # AdvertisingManager
        if not hasattr(cls, '_instances'):
            cls._instances = cls._instances = {}
        if adapter_addr in cls._instances:
            return cls._instances[adapter_addr]

        this_inst = super().__new__(cls, *args, **kwargs)
        cls._instances[adapter_addr] = this_inst
        return this_inst

    def __init__(self, adapter_addr=None):
        # We don't want to re-initialise the AdvertisingManager if
        # it has already been done
        if not hasattr(self, '_client'):
            self._client = gio_dbus.DBusManager()
            if adapter_addr is None:
                adapters = adapter.list_adapters()
                if len(adapters) > 0:
                    adapter_addr = adapters[0]
            use_adapter = adapter.Adapter(adapter_addr)
            if not use_adapter.discoverable:
                use_adapter.discoverable = True
            self.advert_mngr_path = use_adapter.path
            self.advert_mngr_methods = self._client.get_iface_proxy(
                self.advert_mngr_path, constants.LE_ADVERTISING_MANAGER_IFACE)
            self.advert_mngr_props = self._client.get_prop_proxy(
                self.advert_mngr_path)

    def register_advertisement(self, advertisement, options):
        """
        Registers an advertisement object to be sent over the LE
        Advertising channel
        :param advertisement: Advertisement object
        :param options:
        :return:
        """
        self.advert_mngr_methods.RegisterAdvertisement(
            '(oa{sv})',
            advertisement.path,
            options
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
            '(o)',
            advertisement.path
        )


if __name__ == '__main__':
    # Simple test
    beacon = Advertisement(1, 'broadcast')
    beacon.service_UUIDs = ['FEAA']
    beacon.service_data = {'FEAA': [0x10, 0x08, 0x03, 0x75, 0x6B,
                                    0x42, 0x61, 0x7A, 0x2e, 0x67,
                                    0x69, 0x74, 0x68, 0x75, 0x62,
                                    0x2E, 0x69, 0x6F]}
    beacon.start()
    ad_manager = AdvertisingManager()
    ad_manager.register_advertisement(beacon, {})
