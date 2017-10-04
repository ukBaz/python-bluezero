"""Classes that represent the GATT features of a remote device."""

from time import sleep

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

from bluezero import adapter
from bluezero import device
from bluezero import GATT

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


class Central:
    """Create a BLE instance taking the Central role."""

    def __init__(self, device_addr, adapter_addr=None):
        if adapter_addr is None:
            self.dongle = adapter.Adapter()
            logger.debug('Adapter is: {}'.format(self.dongle.address))
        else:
            self.dongle = adapter.Adapter(adapter_addr)
        if not self.dongle.powered:
            self.dongle.powered = True
            logger.debug('Adapter was off, now powered on')
        self.rmt_device = device.Device(self.dongle.address, device_addr)

        self._characteristics = []

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
            chrc.resolve_gatt()

    @property
    def services_resolved(self):
        return self.rmt_device.services_resolved

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.rmt_device.connected

    def connect(self, profile=None):
        """
        Initiate a connection to the remote device and load
        GATT database once resolved

        :param profile: (optional) profile to use for the connection.
        """
        if profile is None:
            self.rmt_device.connect()
        else:
            self.rmt_device.connect(profile)
        while not self.rmt_device.services_resolved:
            sleep(0.5)
        self.load_gatt()

    def disconnect(self):
        """Disconnect from the remote device."""
        self.rmt_device.disconnect()

    def run(self):
        self.dongle.run()

    def quit(self):
        self.dongle.quit()
