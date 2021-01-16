"""Classes required to create a Bluetooth Peripheral."""

# python-bluezero imports
from bluezero import adapter
from bluezero import advertisement
from bluezero import async_tools
from bluezero import localGATT
from bluezero import GATT
from bluezero import tools


logger = tools.create_module_logger(__name__)


class Peripheral:
    """Create a Bluetooth BLE Peripheral"""
    def __init__(self, adapter_address, local_name=None, appearance=None):
        self.app = localGATT.Application()
        self.srv_mng = GATT.GattManager(adapter_address)
        self.services = []
        self.characteristics = []
        self.descriptors = []
        self.primary_services = []
        self.dongle = adapter.Adapter(adapter_address)
        self.local_name = local_name
        self.appearance = appearance
        self.advert = advertisement.Advertisement(1, 'peripheral')
        self.ad_manager = advertisement.AdvertisingManager(adapter_address)
        self.mainloop = async_tools.EventLoop()

    def add_service(self, srv_id, uuid, primary):
        """Add the informatoin required """
        self.services.append(localGATT.Service(srv_id, uuid, primary))
        if primary:
            self.primary_services.append(uuid)

    def add_characteristic(self, srv_id, chr_id, uuid, value,
                           notifying, flags,
                           read_callback=None, write_callback=None,
                           notify_callback=None):
        """Add information for characteristic. srv_id must refer to already
        added service"""
        self.characteristics.append(localGATT.Characteristic(
            srv_id, chr_id, uuid, value, notifying, flags,
            read_callback, write_callback, notify_callback
        ))

    def add_descriptor(self, srv_id, chr_id, dsc_id, uuid, value, flags):
        """Add information for the GATT descriptor. srv_id and chr_id must
        refer to already added service-characteristic hierarchy that this is
        to be added under"""
        self.descriptors.append(localGATT.Descriptor(
            srv_id, chr_id, dsc_id, uuid, value, flags
        ))

    def _create_advertisement(self):
        self.advert.service_UUIDs = self.primary_services
        if self.local_name:
            self.advert.local_name = self.local_name
        if self.appearance:
            self.advert.appearance = self.appearance

    def publish(self):
        """Create advertisement and make peripheral visible"""
        for service in self.services:
            self.app.add_managed_object(service)
        for chars in self.characteristics:
            self.app.add_managed_object(chars)
        for desc in self.descriptors:
            self.app.add_managed_object(desc)
        self._create_advertisement()
        if not self.dongle.powered:
            self.dongle.powered = True
        self.srv_mng.register_application(self.app, {})
        self.ad_manager.register_advertisement(self.advert, {})

        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            self.mainloop.quit()
            self.ad_manager.unregister_advertisement(self.advert)
