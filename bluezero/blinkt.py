"""
This is a simple API to access the Pimoroni Blinkt device.
This is the central API. The peripheral is created with
examples/level100/blinkt_ble.py

"""
from time import sleep
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

from bluezero import central


BLINKT_SRV = '0000FFF0-0000-1000-8000-00805F9B34FB'
BLINKT_CHRC = '0000FFF3-0000-1000-8000-00805F9B34FB'

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


class BLE_blinkt:
    """
    Class to simplify interacting with a microbit over Bluetooth Low Energy
    """
    def __init__(self, device_addr, adapter_addr=None):
        """
        Initialization of an instance of a remote Blinkt BLE device
        :param device_addr: Connect to an already found BLE device with this
                            mac address
        :param adapter_addr: Connect to the BLE device using this adapter.
                             If no adapter specified then first one in
                             list is used
        """
        self.blinkt_dev = central.Central(adapter_addr=adapter_addr,
                                          device_addr=device_addr)
        self.blinkt_data = self.blinkt_dev.add_characteristic(BLINKT_SRV,
                                                              BLINKT_CHRC)

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.blinkt_dev.connected

    def connect(self):
        """
        Connect to the specified Blinkt BLE for this instance
        """
        self.blinkt_dev.connect()
        while not self.blinkt_dev.services_resolved:
            sleep(0.5)
        self.blinkt_dev.load_gatt()

    def disconnect(self):
        """
        Disconnect from the Blinkt BLE device
        """
        self.blnkt_dev.disconnect()

    def _set_all(self, red, green, blue):
        """
        Utility function to handle writing to all pixels at the same time
        :param red: Integer between 0 - 255
        :param green: Integer between 0 - 255
        :param blue: Integer between 0 - 255
        """
        self.blinkt_data.value = [0x06, 0x01, red, green, blue]

    def set_all(self, red, green, blue):
        """
        Set the RGB value of all pixels at the same time.
        :param red: Integer between 0 - 255
        :param green: Integer between 0 - 255
        :param blue: Integer between 0 - 255
        """
        self._set_all(red, green, blue)

    def clear_all(self):
        """
        Switch off all pixels
        """
        self._set_all(0x00, 0x00, 0x00)

    def set_pixel(self, pixel, red, green, blue):
        """
        Set the colour of individual pixels on Blinkt
        :param pixel: integer in range 1 to 8
        :param red: integer in range 0 to 255
        :param green: integer in range 0 to 255
        :param blue: integer in range 0 to 255
        """
        self.blinkt_data.value = [0x07, 0x02, 0x00, pixel, red, green, blue]
