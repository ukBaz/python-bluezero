"""
This is a simple example of how to read data from a micro:bit.

You will need the Bluetooth services of the micro:bit exposed.

This code was developed using the 'Bluetooth Most Services, No Security'
micro:bit hex file from:
http://bluetooth-mdw.blogspot.co.uk/p/bbc-microbit.html

"""
import argparse
import dbus
from time import sleep

from gpiozero import LED
from gpiozero import Buzzer

from bluezero import constants
from bluezero import tools
from bluezero import adapter

# constants
led1 = LED(22)
led2 = LED(23)
led3 = LED(24)
buzz = Buzzer(5)
BEEP_TIME = 0.25


class microbit:
    """
    Class to introspect Bluez to find the paths for required UUIDs
    """
    def __init__(self, address):
        self.bus = dbus.SystemBus()
        self.address = address
        # Device Information
        self.device_path = tools.get_dbus_path(constants.DEVICE_INTERFACE,
                                               'Address',
                                               self.address)[0]
        self.remote_device_obj = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.device_path)
        self.remote_device_methods = dbus.Interface(
            self.remote_device_obj,
            constants.DEVICE_INTERFACE)
        self.remote_device_props = dbus.Interface(self.remote_device_obj,
                                                  dbus.PROPERTIES_IFACE)
        # Button Service
        self.btn_srv_uuid = 'E95D9882-251D-470A-A062-FA1922DFA9A8'
        self.btn_srv_path = None
        # Button A
        self.btn_a_chr_uuid = 'E95DDA90-251D-470A-A062-FA1922DFA9A8'
        self.btn_a_chr_path = None
        # Button B
        self.btn_b_chr_uuid = 'E95DDA91-251D-470A-A062-FA1922DFA9A8'
        self.btn_b_chr_path = None

    def connect(self):
        self.remote_device_methods.Connect()
        while not self.remote_device_props.Get(
                constants.DEVICE_INTERFACE,
                'ServicesResolved'):
            sleep(0.25)
        self._update_dbus_paths()

    def _update_dbus_paths(self):
        self.btn_srv_path = tools.uuid_dbus_path(constants.GATT_SERVICE_IFACE,
                                                 self.btn_srv_uuid)[0]
        # Button A
        self.btn_a_chr_path = tools.uuid_dbus_path(constants.GATT_CHRC_IFACE,
                                                   self.btn_a_chr_uuid)[0]
        # Button B
        self.btn_b_chr_path = tools.uuid_dbus_path(constants.GATT_CHRC_IFACE,
                                                   self.btn_b_chr_uuid)[0]

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.remote_device_props.Get(
            constants.DEVICE_INTERFACE, 'Connected')

    def disconnect(self):
        self.remote_device_methods.Disconnect()

    def read_button_a(self):
        """
        Helper function to read the state of button A on a micro:bit
        :return: integer representing button value
        """
        return self.read_button(self.btn_a_chr_path)

    def read_button_b(self):
        """
        Helper function to read the state of button B on a micro:bit
        :return: integer representing button value
        """
        return self.read_button(self.btn_b_chr_path)

    def read_button(self, btn_path):
        """
        Read the button characteristic on the micro:bit and return value
        :param bus_obj: Object of bus connected to (System Bus)
        :param bluez_path: The Bluez path to the button characteristic
        :return: integer representing button value
        """

        # Get characteristic interface for data
        btn_obj = self.bus.get_object(constants.BLUEZ_SERVICE_NAME,
                                      btn_path)
        btn_iface = dbus.Interface(btn_obj, constants.GATT_CHRC_IFACE)

        # Read button value
        btn_val = btn_iface.ReadValue(dbus.Array())

        answer = int.from_bytes(btn_val, byteorder='little', signed=False)
        return answer


def central(address):
    dongle = adapter.Adapter(adapter.list_adapters()[0])
    if not dongle.powered:
        dongle.powered = True
    # Find nearby devices
    dongle.nearby_discovery()

    ubit = microbit(address)
    sense_buttons = True

    ubit.connect()

    led2.on()
    buzz.on()
    sleep(BEEP_TIME)
    buzz.off()

    while sense_buttons:
        btn_a = ubit.read_button_a()
        btn_b = ubit.read_button_b()
        # print('Button states: a={} b={}'.format(btn_a, btn_b))
        if btn_a > 0 and btn_b < 1:
            print('Button A')
            led1.on()
            led3.off()
        elif btn_a < 1 and btn_b > 0:
            print('Button B')
            led1.off()
            led3.on()
        elif btn_a > 0 and btn_b > 0:
            sense_buttons = False
            led1.on()
            led3.on()
            buzz.on()
            sleep(BEEP_TIME)
            buzz.off()
            print('Bye bye!!!')
        elif btn_a < 1 and btn_b < 1:
            led1.off()
            led3.off()
        if not ubit.connected:
            sense_buttons = False
            led1.on()
            led2.on()
            led3.on()
            buzz.on()
            sleep(BEEP_TIME)
            buzz.off()

        sleep(0.02)

    # Disconnect device
    ubit.disconnect()

    # Read the connected status property
    led1.off()
    led2.off()
    led3.off()
    buzz.off()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Use micro:bit as remote for Ryanteck TrafficHAT.')
    parser.add_argument('address',
                        help='the address of the micro:bit of interest')

    args = parser.parse_args()
    central(str(args.address))
