"""Classes that represent the GATT features of a remote device."""

from time import sleep

from bluezero import adapter
from bluezero import device
from bluezero import GATT
from bluezero import tools

logger = tools.create_module_logger(__name__)


class Central:
    """Create a BLE instance taking the Central role."""

    def __init__(self, device_addr, adapter_addr=None):
        if adapter_addr is None:
            self.dongle = adapter.Adapter()
            logger.debug('Adapter is: %s', self.dongle.address)
        else:
            self.dongle = adapter.Adapter(adapter_addr)
        if not self.dongle.powered:
            self.dongle.powered = True
            logger.debug('Adapter was off, now powered on')
        self.rmt_device = device.Device(self.dongle.address, device_addr)

        self._characteristics = []

    @staticmethod
    def available(adapter_address=None):
        """Generator for getting a list of devices"""
        return device.Device.available(adapter_address)

    def add_characteristic(self, srv_uuid, chrc_uuid):
        """
        Specify a characteristic of interest on the remote device by using
        the GATT Service UUID and Characteristic UUID

        :param srv_uuid: 128 bit UUID
        :param chrc_uuid: 128 bit UUID
        :return:
        """
        chrc_hndl = GATT.Characteristic(self.dongle.address,
                                        self.rmt_device.address,
                                        srv_uuid,
                                        chrc_uuid)
        self._characteristics.append(chrc_hndl)
        return chrc_hndl

    def load_gatt(self):
        """
        Once the remote device has been connected to and the GATT database
        has been resolved then it needs to be loaded.

        :return:
        """
        for chrc in self._characteristics:
            available = chrc.resolve_gatt()
            if available:
                logger.info('Service: %s and characteristic: %s added',
                            chrc.srv_uuid, chrc.chrc_uuid)
            else:
                logger.warning('Service: %s and characteristic: %s not '
                               'available on device: %s', chrc.srv_uuid,
                               chrc.chrc_uuid, chrc.device_addr)

    @property
    def services_available(self):
        """Get a list of Service UUIDs available on this device"""
        return self.rmt_device.services_available

    @property
    def services_resolved(self):
        """Indicate whether or not service discovery has been resolved"""
        return self.rmt_device.services_resolved

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.rmt_device.connected

    def connect(self, profile=None, timeout=35):
        """
        Initiate a connection to the remote device and load
        GATT database once resolved

        :param profile: (optional) profile to use for the connection.
        :param timeout: (optional) seconds to wait for connection.
        """
        if profile is None:
            self.rmt_device.connect(timeout=timeout)
        else:
            self.rmt_device.connect(profile, timeout=timeout)
        while not self.rmt_device.services_resolved:
            sleep(0.5)
        self.load_gatt()

    def disconnect(self):
        """Disconnect from the remote device."""
        self.rmt_device.disconnect()

    def run(self):
        """Start event loop"""
        self.dongle.run()

    def quit(self):
        """Stop event loop"""
        self.dongle.quit()
