"""
This is a simple example of how to read data from a micro:bit.

It undoubtedly needs polishing and isn't production worthy.
It is however a starting point...

This code assumes you have connected to your micro:bit once already using
bluetoothctl. A video of how to do this is at:
https://youtu.be/QxPsVozglnM

This is needed so that Bluez knows about the micro:bit without having to
do a scan. This code does not do a scan.

"""
import argparse
import dbus
from time import sleep

from gpiozero import LED
from gpiozero import Buzzer

import iterate

# constants

led1 = LED(22)
led2 = LED(23)
led3 = LED(24)
buzz = Buzzer(5)

DBUS_SYS_BUS = dbus.SystemBus()

DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DEVICE_IFACE = 'org.bluez.Device1'
CHAR_IFACE = 'org.bluez.GattCharacteristic1'

BEEP_TIME = 0.25


class microbit:
    """
    Class to introspect Bluez to find the paths for required UUIDs
    """
    def __init__(self, address):
        self.address = address
        iterate.build_introspection(DBUS_SYS_BUS,
                                    'org.bluez',
                                    '/org/bluez/hci0')
        self.device_path = iterate.get_path_for_device(self.address)
        self.btn_srv_uuid = 'E95D9882-251D-470A-A062-FA1922DFA9A8'
        self.btn_srv_path = iterate.get_path_for_uuid(self.address,
                                                      self.btn_srv_uuid,
                                                      'service')
        self.btn_a_chr_uuid = 'E95DDA90-251D-470A-A062-FA1922DFA9A8'
        self.btn_a_chr_path = iterate.get_path_for_uuid(self.address,
                                                        self.btn_a_chr_uuid,
                                                        'characteristic')
        self.btn_b_chr_uuid = 'E95DDA91-251D-470A-A062-FA1922DFA9A8'
        self.btn_b_chr_path = iterate.get_path_for_uuid(self.address,
                                                        self.btn_b_chr_uuid,
                                                        'characteristic')


def val_print(obj_prop, value):
    """
    Print out a string and a value
    :param obj_prop: Descriptive string
    :param value: Value to be printed
    """
    print('{0}: {1}'.format(obj_prop, value))


def read_button_a(ubit):
    """
    Helper function to read the state of button A on a micro:bit
    :return: integer representing button value
    """
    return read_button(DBUS_SYS_BUS, ubit.btn_a_chr_path)


def read_button_b(ubit):
    """
    Helper function to read the state of button B on a micro:bit
    :return: integer representing button value
    """
    return read_button(DBUS_SYS_BUS, ubit.btn_b_chr_path)


def read_button(bus_obj, bluez_path):
    """
    Read the button characteristic on the micro:bit and return value
    :param bus_obj: Object of bus connected to (System Bus)
    :param bluez_path: The Bluez path to the button characteristic
    :return: integer representing button value
    """

    # Get characteristic interface for data
    data_iface = dbus.Interface(bus_obj.get_object(BLUEZ_SERVICE_NAME,
                                                   bluez_path),
                                CHAR_IFACE)
    # Read button value
    btn_val = data_iface.ReadValue(dbus.Array())

    answer = int.from_bytes(btn_val, byteorder='little', signed=False)
    return answer


def central(address):

    ubit = microbit(address)
    sense_buttons = True

    # Get device property interface
    dev_props = dbus.Interface(DBUS_SYS_BUS.get_object(BLUEZ_SERVICE_NAME,
                                                       ubit.device_path),
                               DBUS_PROP_IFACE)
    # Get Bluez device interface
    dev_iface = dbus.Interface(DBUS_SYS_BUS.get_object(BLUEZ_SERVICE_NAME,
                                                       ubit.device_path),
                               DEVICE_IFACE)

    # Connect to device
    dev_iface.Connect()

    # Read the connected status property
    fetch_prop = 'Connected'
    device_data = dev_props.Get(DEVICE_IFACE, fetch_prop)
    val_print(fetch_prop, device_data)
    led2.on()
    buzz.on()
    sleep(BEEP_TIME)
    buzz.off()

    while sense_buttons:
        btn_a = read_button_a(ubit)
        btn_b = read_button_b(ubit)
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
        if dev_props.Get(DEVICE_IFACE, 'Connected') != 1:
            sense_buttons = False
            led1.on()
            led2.on()
            led3.on()
            buzz.on()
            sleep(BEEP_TIME)
            buzz.off()

        sleep(0.02)

    # Disconnect device
    dev_iface.Disconnect()

    # Read the connected status property
    fetch_prop = 'Connected'
    device_data = dev_props.Get(DEVICE_IFACE, fetch_prop)
    val_print(fetch_prop, device_data)
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
    central(args.address)
