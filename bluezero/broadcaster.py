"""
The level 10 file for creating beacons
This requires BlueZ to have the experimental flag set
"""
from bluezero import adapter
from bluezero import advertisement


class Beacon:
    """
    Create a non-connectable Bluetooth instance advertising information
    """
    def __init__(self, adapter_addr=None):
        """Default initialiser.

        Creates the BLE beacon object
        If an adapter object exists then give it as an optional argument
        If an adapter object is not given then the first adapter found is used

        :param adapter_addr: Optional Python adapter object.
        """
        self.dongle = None
        if adapter_addr is None:
            self.dongle = adapter.Adapter(adapter.list_adapters()[0])
        else:
            self.dongle = adapter.Adapter(adapter_addr)

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
        :param data: Data to be sent (Limit of 23bytes) e.g. b'\\xff' * 23
        """
        if isinstance(manufacturer, str):
            manufacturer = int(manufacturer, 16)
        self.broadcaster.manufacturer_data(manufacturer, data)

    def include_tx_power(self, show_power=None):
        """
        Use to include TX power in advertisement.
        This is different to the TX power in specific beacon format
        (e.g. Eddystone)

        :param show_power: boolean value
        :return:
        """
        if show_power is None:
            return self.broadcaster.include_tx_power
        else:
            self.broadcaster.include_tx_power = show_power

    def start_beacon(self):
        """
        Start beacon advertising
        """
        if not self.dongle.powered:
            self.dongle.powered = True
        ad_manager = advertisement.AdvertisingManager(self.dongle.address)
        ad_manager.register_advertisement(self.broadcaster, {})

        try:
            self.broadcaster.start()
        except KeyboardInterrupt:
            self.broadcaster.stop()
            ad_manager.unregister_advertisement(self.broadcaster)
        finally:
            pass
