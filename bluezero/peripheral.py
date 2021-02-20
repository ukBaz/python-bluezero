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
        """
        Add the service information required

        :param srv_id: integer between 0 & 9999 as unique reference
        :param uuid: The Bluetooth uuid number for this service
        :param primary: boolean for if this service should be advertised

        """
        self.services.append(localGATT.Service(srv_id, uuid, primary))
        if primary:
            self.primary_services.append(uuid)

    def add_characteristic(self, srv_id, chr_id, uuid, value,
                           notifying, flags,
                           read_callback=None, write_callback=None,
                           notify_callback=None):
        """
        Add information for characteristic.

        :param srv_id: integer of parent service that was added
        :param chr_id: integer between 0 & 9999 as unique reference
        :param uuid: The Bluetooth uuid number for this characteristic
        :param value: Initial value. list of integers in little endian format
        :param notifying: Boolean representing initial state of notifications
        :param flags: Defines how the characteristic value can be used. See
            Core spec "Table 3.5: Characteristic Properties bit field", and
            "Table 3.8: Characteristic Extended. Properties bit field".
            Allowed values:

            - "broadcast"
            - "read"
            - "write-without-response"
            - "write"
            - "notify"
            - "indicate"
            - "authenticated-signed-writes"
            - "extended-properties"
            - "reliable-write"
            - "writable-auxiliaries"
            - "encrypt-read"
            - "encrypt-write"
            - "encrypt-authenticated-read"
            - "encrypt-authenticated-write"
            - "secure-read" (Server only)
            - "secure-write" (Server only)
            - "authorize"

        :param read_callback: function to be called when read_value is called
            by client. function should return python list of integers
            representing new value of characteristic
        :param write_callback: function to be called when write_value is called
            by client. Function should have two parameters value and options.
            value is python list of integers with new value of characteristic.
        :param notify_callback: function to be called when notify_start or
            notify_stop is called by client. Function should have two
            parameters notifying and characteristic. The `characteristic`
            is the instantiation of a localGAT.Characteristic class

        """
        self.characteristics.append(localGATT.Characteristic(
            srv_id, chr_id, uuid, value, notifying, flags,
            read_callback, write_callback, notify_callback
        ))

    def add_descriptor(self, srv_id, chr_id, dsc_id, uuid, value, flags):
        """
        Add information for the GATT descriptor.

        :param srv_id: integer of parent service that was added
        :param chr_id: integer of parent characteristic that was added
        :param dsc_id: integer between 0 & 9999 as unique reference
        :param uuid: The Bluetooth uuid number for this characteristic
        :param value: Initial value. list of integers in little endian format
        :param flags: Defines how the descriptor value can be used.
            Possible values:

                - "read"
                - "write"
                - "encrypt-read"
                - "encrypt-write"
                - "encrypt-authenticated-read"
                - "encrypt-authenticated-write"
                - "secure-read" (Server Only)
                - "secure-write" (Server Only)
                - "authorize"

        """
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

    @property
    def on_connect(self):
        """
        Callback for when a device connects to the peripheral.
        Callback can accept 0, 1, or 2 positional arguments
        1: a device.Device instance of the connected target
        2: the local adapter address followed by the remote address
        """
        return self.dongle.on_connect

    @on_connect.setter
    def on_connect(self, callback):
        self.dongle.on_connect = callback

    @property
    def on_disconnect(self):
        """
        Callback for when a device disconnects from the peripheral.
        Callback can accept 0, 1, or 2 positional arguments
        1: a device.Device instance of the disconnected target
        2: the local adapter address followed by the remote address
        """
        return self.dongle.on_disconnect

    @on_disconnect.setter
    def on_disconnect(self, callback):
        self.dongle.on_disconnect = callback
