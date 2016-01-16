"""
This is a simple example of how to read the Ti Sensortag CC2650.

The idea of this file is to show as simplified as possibly
procedure. Hopefully this short file will give clarity and
understanding on how to access the properties and methods
of Bluez D-Bus interface for a Ti Sensortag.

The information for the CC2650 comes from:
http://processors.wiki.ti.com/index.php/CC2650_SensorTag_User%27s_Guide

This program makes some assumptions to keep the complexity down:
1) The paths to characteristics are known
2) The adapter is hci0
3) A scan has happened and the sensortag is in the device list
   (Probably true as you will have had to get the paths to characteristics)
4) You are running Bluez 5.36 or higher (with the experimental flag)
"""
# dbus-python is a binding for libdbus, the reference implementation of D-Bus
import dbus

# constants
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DEVICE_IFACE = 'org.bluez.Device1'
DEVICE_OBJECT_PATH = '/org/bluez/hci0/dev_B0_B4_48_BE_5D_83'
CHAR_IFACE = 'org.bluez.GattCharacteristic1'
TMP_CONF_PATH = DEVICE_OBJECT_PATH + '/service001f/char0023'
TMP_DATA_PATH = DEVICE_OBJECT_PATH + '/service001f/char0020'
OPT_CONF_PATH = DEVICE_OBJECT_PATH + '/service003f/char0043'
OPT_DATA_PATH = DEVICE_OBJECT_PATH + '/service003f/char0040'
BAR_CONF_PATH = DEVICE_OBJECT_PATH + '/service002f/char0033'
BAR_DATA_PATH = DEVICE_OBJECT_PATH + '/service002f/char0030'
HUM_CONF_PATH = DEVICE_OBJECT_PATH + '/service0027/char002b'
HUM_DATA_PATH = DEVICE_OBJECT_PATH + '/service0027/char0028'


def val_print(obj_prop, value):
    """
    Print out a string and a value
    :param obj_prop: Descriptive string
    :param value: Value to be printed
    """
    print('{0}: {1}'.format(obj_prop, value))


def read_sensor(bus_obj, config_path, data_path):
    """
    Read the sensors on the cc2650.
    Does this by turning on the sensor, reads and then turns off sensor.
    :param bus_obj: Object of bus connected to
    :param config_path: The path to the configuration characteristic
    :param data_path: The path to the data characteristic
    :return:
    """
    # Get property interface
    char_props = dbus.Interface(bus_obj.get_object(BLUEZ_SERVICE_NAME,
                                                   data_path),
                                DBUS_PROP_IFACE)
    # Read UUID property
    fetch_prop = 'UUID'
    service_data = char_props.Get(CHAR_IFACE, fetch_prop)
    val_print(fetch_prop, service_data)

    # Get characteristic interface for configuration
    conf_iface = dbus.Interface(bus_obj.get_object(BLUEZ_SERVICE_NAME,
                                                   config_path),
                                CHAR_IFACE)
    # Get characteristic interface for data
    data_iface = dbus.Interface(bus_obj.get_object(BLUEZ_SERVICE_NAME,
                                                   data_path),
                                CHAR_IFACE)
    # Set configuration value to 1 (enable sensor)
    conf_val = conf_iface.ReadValue()
    val_print('Config', int(conf_val[0]))
    conf_iface.WriteValue(dbus.Array([dbus.Byte(1)],
                                     signature=dbus.Signature('y')))
    conf_val = conf_iface.ReadValue()
    val_print('Config', int(conf_val[0]))

    # Read sensor data
    opt_val = data_iface.ReadValue()
    val_print('Raw Value', opt_val)

    # set configuraton value to 0 (disable sensor)
    conf_iface.WriteValue(dbus.Array([dbus.Byte(0)],
                                     signature=dbus.Signature('y')))
    conf_val = conf_iface.ReadValue()
    val_print('Config', int(conf_val[0]))


def client():
    bus = dbus.SystemBus()

    # Get device property interface
    dev_props = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME,
                                              DEVICE_OBJECT_PATH),
                               DBUS_PROP_IFACE)
    # Get device interface
    dev_iface = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME,
                                              DEVICE_OBJECT_PATH),
                               DEVICE_IFACE)

    # Connect to device
    dev_iface.Connect()

    # Read the connected status property
    fetch_prop = 'Connected'
    device_data = dev_props.Get(DEVICE_IFACE, fetch_prop)
    val_print(fetch_prop, device_data)

    if device_data == 1:
        # IR Temperature Sensor
        read_sensor(bus, TMP_CONF_PATH, TMP_DATA_PATH)
        # Optical Sensor
        read_sensor(bus, OPT_CONF_PATH, OPT_DATA_PATH)
        # Barometric Pressure Sensor
        read_sensor(bus, BAR_CONF_PATH, BAR_DATA_PATH)
        # Humidity Sensor
        read_sensor(bus, HUM_CONF_PATH, HUM_DATA_PATH)

    # Disconnect device
    dev_iface.Disconnect()


if __name__ == '__main__':
    client()
