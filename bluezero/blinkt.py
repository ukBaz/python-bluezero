"""
This is a simple API to access the Pimoroni Blinkt device.
This is the central API. The peripheral is created with
examples/level100/blinkt_ble.py

"""
from time import sleep
import logging

from bluezero import constants
from bluezero import tools
from bluezero import adapter
from bluezero import device


BLINKT_SRV = '0000FFF0-0000-1000-8000-00805F9B34FB'
BLINKT_CHRC = '0000FFF3-0000-1000-8000-00805F9B34FB'

logging.basicConfig(level=logging.DEBUG)

class BLE_blinkt:
    """
    Class to simplify interacting with a microbit over Bluetooth Low Energy
    """
    def __init__(self, name=None, address=None):
        """
        Initialization of an instance of a remote microbit
        :param name: Will look for a BLE device with this string in its name
        :param address: Will look for a BLE device with this address
         (Currently not implemented)
        """
        self.name = name
        self.address = address
        self.dongle = adapter.Adapter(adapter.list_adapters()[0])
        if not self.dongle.powered:
            self.dongle.powered = True
        logging.debug('Adapter powered')
        logging.debug('Start discovery')
        self.dongle.nearby_discovery()
        self.ubit = device.Device(
            tools.get_dbus_path(
                constants.DEVICE_INTERFACE,
                'Name',
                name)[0])

        self.blinkt_srv_path = None
        self.blinkt_chrc_path = None

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.ubit.connected

    def connect(self):
        """
        Connect to the specified microbit for this instance
        """
        self.ubit.connect()
        while not self.ubit.services_resolved:
            sleep(0.5)
        self._get_dbus_paths()

    def _get_dbus_paths(self):
        """
        Utility function to get the paths for UUIDs
        :return:
        """
        self.blinkt_srv_path = tools.uuid_dbus_path(
            constants.GATT_SERVICE_IFACE,
            BLINKT_SRV)[0]
        self.blinkt_chrc_path = tools.uuid_dbus_path(
            constants.GATT_CHRC_IFACE,
            BLINKT_CHRC)[0]
        self.blinkt_obj = tools.get_dbus_obj(constants.BLUEZ_SERVICE_NAME,
                                             self.blinkt_chrc_path)

        self.blinkt_iface = tools.get_dbus_iface(constants.GATT_CHRC_IFACE,
                                                 self.blinkt_obj)

    def disconnect(self):
        """
        Disconnect from the microbit
        """
        self.ubit.disconnect()

    def _set_all(self, red, green, blue):
        self.blinkt_iface.WriteValue([0x06, 0x01, red, green, blue], ())

    def set_all(self, red, green, blue):
        self._set_all(red, green, blue)

    def clear_all(self):
        self._set_all(0x00, 0x00, 0x00)

    def set_pixel(self, pixel, red, green, blue):
        self.blinkt_iface.WriteValue([0x07, 0x02, 0x00,
                                     pixel, red, green, blue], ())
