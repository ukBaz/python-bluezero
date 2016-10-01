"""
This is a simple example of how to read the Ti Sensortag CC2650.

The idea of this file is to show as simplified as possibly
procedure. Hopefully this short file will give clarity and
understanding on how to access the properties and methods
of Bluez D-Bus interface for a Ti Sensortag.

The information for the CC2650 comes from:
http://processors.wiki.ti.com/index.php/CC2650_SensorTag_User%27s_Guide

This program makes some assumptions to keep the complexity down:
1) The adapter is the first one in the list of adapters
    (normally there is only one)
2) You are running Bluez 5.42 or higher
"""
from time import sleep

from bluezero import tools
from bluezero import constants
from bluezero import adapter
from bluezero import device
from bluezero.GATT import Characteristic


def val_print(obj_prop, value):
    """
    Print out a string and a value
    :param obj_prop: Descriptive string
    :param value: Value to be printed
    """
    print('{0}: {1}'.format(obj_prop, value))


def read_sensor(config_path, data_path):
    """
    Read the sensors on the cc2650.
    Does this by turning on the sensor, reads and then turns off sensor.
    :param config_path: The path to the configuration characteristic
    :param data_path: The path to the data characteristic
    :return:
    """
    # Set configuration value to 1 (enable sensor)
    conf_val = config_path.read_raw_value()
    val_print('Sensor enabled', conf_val)
    config_path.write_value((1).to_bytes(1, byteorder='little'))
    conf_val = config_path.read_raw_value()
    val_print('Sensor enabled', conf_val)

    # Read sensor data
    opt_val = data_path.read_raw_value()
    val_print('Raw Value', opt_val)

    # set configuraton value to 0 (disable sensor)
    config_path.read_raw_value()
    config_path.write_value((0).to_bytes(1, byteorder='little'))
    conf_val = config_path.read_raw_value()
    val_print('Sensor enabled', conf_val)


def client():
    dongle = adapter.Adapter(adapter.list_adapters()[0])
    if not dongle.powered:
        dongle.powered = True

    dongle.nearby_discovery()
    cc2650 = device.Device(tools.device_dbus_path(constants.DEVICE_INTERFACE,
                                                  'SensorTag')[0])
    # Connect to device
    cc2650.connect()

    while not cc2650.services_resolved:
        sleep(0.5)

    # constants
    TMP_CONF_PATH = Characteristic(tools.uuid_dbus_path(
        constants.GATT_CHRC_IFACE,
        'F000AA02-0451-4000-B000-000000000000')[0])
    TMP_DATA_PATH = Characteristic(tools.uuid_dbus_path(
        constants.GATT_CHRC_IFACE,
        'F000AA01-0451-4000-B000-000000000000')[0])
    OPT_CONF_PATH = Characteristic(tools.uuid_dbus_path(
        constants.GATT_CHRC_IFACE,
        'F000AA72-0451-4000-B000-000000000000')[0])
    OPT_DATA_PATH = Characteristic(tools.uuid_dbus_path(
        constants.GATT_CHRC_IFACE,
        'F000AA71-0451-4000-B000-000000000000')[0])
    BAR_CONF_PATH = Characteristic(tools.uuid_dbus_path(
        constants.GATT_CHRC_IFACE,
        'F000AA42-0451-4000-B000-000000000000')[0])
    BAR_DATA_PATH = Characteristic(tools.uuid_dbus_path(
        constants.GATT_CHRC_IFACE,
        'F000AA41-0451-4000-B000-000000000000')[0])
    HUM_CONF_PATH = Characteristic(tools.uuid_dbus_path(
        constants.GATT_CHRC_IFACE,
        'F000AA22-0451-4000-B000-000000000000')[0])
    HUM_DATA_PATH = Characteristic(tools.uuid_dbus_path(
        constants.GATT_CHRC_IFACE,
        'F000AA21-0451-4000-B000-000000000000')[0])

    # Read the connected status property
    if cc2650.connected:
        # IR Temperature Sensor
        print('\nIR Temperature Sensor')
        read_sensor(TMP_CONF_PATH, TMP_DATA_PATH)
        # Optical Sensor
        print('\nOptical Sensor')
        read_sensor(OPT_CONF_PATH, OPT_DATA_PATH)
        # Barometric Pressure Sensor
        print('\nBarometric Pressure Sensor')
        read_sensor(BAR_CONF_PATH, BAR_DATA_PATH)
        # Humidity Sensor
        print('\nHumidity Sensor')
        read_sensor(HUM_CONF_PATH, HUM_DATA_PATH)

    # Disconnect device
    cc2650.disconnect()


if __name__ == '__main__':
    client()
