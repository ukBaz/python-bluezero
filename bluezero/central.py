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


def generic_error_cb(error):
    """Generic Error Callback function."""
    logger.error('D-Bus call failed: ' + str(error))
    mainloop.quit()


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
        chrc_hndl = GATT.Characteristic(self.dongle.address,
                                        self.rmt_device.address,
                                        srv_uuid,
                                        chrc_uuid)
        self._characteristics.append(chrc_hndl)
        return chrc_hndl

    def load_gatt(self):
        for chrc in self._characteristics:
            chrc.resolve_gatt()

    def read_value(self, chrc_name):
        return self.chrc_objs[chrc_name].value

    @property
    def services_resolved(self):
        return self.rmt_device.services_resolved

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.rmt_device.connected

    def connect(self, profile=None):
        """
        Initiate a connection to the remote device.

        :param address: unused
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
