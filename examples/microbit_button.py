"""
This is a simple example of how to read data from a micro:bit.

It undoubtedly needs polishing and isn't production worthy.
It is however a starting point...

You will need to use a tool like 'bluetoothctl' to find the paths
for your specific micro:bit.

The next version of this example should look to do more introspection
to get these path values rather than being constants in the code

"""
import dbus
from time import sleep

from gpiozero import LED
from gpiozero import Buzzer

led1 = LED(22)
led2 = LED(23)
led3 = LED(24)
buzz = Buzzer(5)

# constants
DBUS_SYS_BUS = dbus.SystemBus()

DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DEVICE_IFACE = 'org.bluez.Device1'
CHAR_IFACE = 'org.bluez.GattCharacteristic1'

UBIT_DEVICE_PATH = '/org/bluez/hci0/dev_E8_A9_41_CE_31_5A'
UBIT_BTN_SRV_UUID = 'E95D9882-251D-470A-A062-FA1922DFA9A8'
UBIT_BTN_SRV_PATH = UBIT_DEVICE_PATH + '/service002f'
UBIT_BTN_A_CHR_UUID = 'E95DDA90-251D-470A-A062-FA1922DFA9A8'
UBIT_BTN_A_CHR_PATH = UBIT_DEVICE_PATH + '/service002f/char0030'
UBIT_BTN_B_CHR_UUID = 'E95DDA91-251D-470A-A062-FA1922DFA9A8'
UBIT_BTN_B_CHR_PATH = UBIT_DEVICE_PATH + '/service002f/char0033'

BEEP_TIME = 0.25


def val_print(obj_prop, value):
    """
    Print out a string and a value
    :param obj_prop: Descriptive string
    :param value: Value to be printed
    """
    print('{0}: {1}'.format(obj_prop, value))


def read_button_a():
    """

    :return:
    """
    return read_button(DBUS_SYS_BUS, UBIT_BTN_A_CHR_PATH)


def read_button_b():
    return read_button(DBUS_SYS_BUS, UBIT_BTN_B_CHR_PATH)


def read_button(bus_obj, bluez_path):
    """
    Read the button service on the micro:bit and return value
    :param bus_obj: Object of bus connected to (System bus)
    :param bluez_path: The path to the data characteristic
    :return: integer representing button value
    """
    # Get property interface
    char_props = dbus.Interface(bus_obj.get_object(BLUEZ_SERVICE_NAME,
                                                   bluez_path),
                                DBUS_PROP_IFACE)
    # Read UUID property
    fetch_prop = 'UUID'
    uuid = char_props.Get(CHAR_IFACE, fetch_prop)

    # Get characteristic interface for data
    data_iface = dbus.Interface(bus_obj.get_object(BLUEZ_SERVICE_NAME,
                                                   bluez_path),
                                CHAR_IFACE)
    # Read button value
    opt_val = data_iface.ReadValue(dbus.Array())

    answer = int.from_bytes(opt_val, byteorder='little', signed=False)
    # print('Button return value: ', answer)
    return answer


def central():

    sense_buttons = True

    # Get device property interface
    dev_props = dbus.Interface(DBUS_SYS_BUS.get_object(BLUEZ_SERVICE_NAME,
                                                       UBIT_DEVICE_PATH),
                               DBUS_PROP_IFACE)
    # Get device interface
    dev_iface = dbus.Interface(DBUS_SYS_BUS.get_object(BLUEZ_SERVICE_NAME,
                                                       UBIT_DEVICE_PATH),
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
        btn_a = read_button_a()
        btn_b = read_button_b()
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
    central()
