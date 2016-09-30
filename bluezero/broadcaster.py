"""
The level 10 file for creating beacons
"""
from bluezero import tools
from bluezero import adapter
from bluezero import constants
from bluezero import advertisement


class Beacon:
    """
    Create a non-connectable Bluetooth instance advertising information
    """
    def __init__(self, adapter_obj=None):
        """Default initialiser.

        Creates the BLE beacon object
        If an adapter object exists then give it as an optional argument
        If an adapter object is not given then the first adapter found is used
        :param adapter_obj: Optional Python adapter object.
        """
        self.dongle = None
        if adapter_obj is None:
            self.dongle = adapter.Adapter(adapter.list_adapters()[0])
        else:
            self.dongle = adapter_obj

        self.broadcaster = advertisement.Advertisement(1, 'broadcast')

    def add_service_data(self, service, data):
        """
        Add service and service data to be used in beacon message
        :param service: Valid service UUID
        :param data: Data to be sent (Limit of ??)
        """
        self.broadcaster.service_UUIDs = [service]
        self.broadcaster.service_data = {service: data}

    def add_manufacturer_data(self, manufacturer, data):
        """
        Add manufacturer information to be used in beacon message
        :param manufacturer: Use numbers from Bluetooth SIG
        https://www.bluetooth.com/specifications/assigned-numbers/16-bit-UUIDs-for-Members
        :param data: Data to be sent (Limit of ??)
        """
        pass

    def include_tx_power(self, show_power=None):
        """
        Use to include TX power in advertisement.
        This is different to the TX power in specific beacon format
        (e.g. Eddystone)
        :param show_power:
        :return:
        """
        if show_power is None:
            self.broadcaster.Get(constants.LE_ADVERTISEMENT_IFACE,
                                 'IncludeTxPower')
        else:
            self.broadcaster.Set(constants.LE_ADVERTISEMENT_IFACE,
                                 'IncludeTxPower',
                                 show_power)

    def start_beacon(self):
        """
        Start beacon advertising
        """
        if not self.dongle.powered:
            self.dongle.powered = True
        ad_manager = advertisement.AdvertisingManager(self.dongle.path)
        ad_manager.register_advertisement(self.broadcaster, {})

        try:
            tools.start_mainloop()
        except KeyboardInterrupt:
            tools.stop_mainloop()
            ad_manager.unregister_advertisement(self.broadcaster)
        finally:
            pass
