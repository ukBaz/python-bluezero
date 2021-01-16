"""Example of how to create a Peripheral device/GATT Server"""
# Standard modules
import logging
import random

# Bluezero modules
from bluezero import async_tools
from bluezero import adapter
from bluezero import peripheral

# constants
# Custom service uuid
CPU_TMP_SRVC = '12341000-1234-1234-1234-123456789abc'
# https://www.bluetooth.com/specifications/assigned-numbers/
# Bluetooth SIG adopted UUID for Temperature characteristic
CPU_TMP_CHRC = '2A6E'
# Bluetooth SIG adopted UUID for Characteristic Presentation Format
CPU_FMT_DSCP = '2904'


def read_value():
    """
    Example read callback. Value returned needs to a list of bytes/integers
    in little endian format.

    This one does a mock reading CPU temperature callback.
    Return list of integer values.
    Bluetooth expects the values to be in little endian format and the
    temperature characteristic to be an sint16 (signed & 2 octets) and that
    is what dictates the values to be used in the int.to_bytes method call.

    :return: list of uint8 values
    """
    cpu_value = random.randrange(3200, 5310, 10) / 100
    return list(int(cpu_value * 100).to_bytes(2,
                                              byteorder='little', signed=True))


def update_value(characteristic):
    """
    Example of callback to send notifications

    :param characteristic:
    :return: boolean to indicate if timer should continue
    """
    # read/calculate new value.
    new_value = read_value()
    # Causes characteristic to be updated and send notification
    characteristic.set_value(new_value)
    # Return True to continue notifying. Return a False will stop notifications
    # Getting the value from the characteristic of if it is notifying
    return characteristic.is_notifying


def notify_callback(notifying, characteristic):
    """
    Noitificaton callback example. In this case used to start a timer event
    which calls the update callback ever 2 seconds

    :param notifying: boolean for start or stop of notifications
    :param characteristic: The python object for this characteristic
    """
    if notifying:
        async_tools.add_timer_seconds(2, update_value, characteristic)


def main(adapter_address):
    """Creation of peripheral"""
    logger = logging.getLogger('localGATT')
    logger.setLevel(logging.DEBUG)
    # Example of the output from read_value
    print('CPU temperature is {}\u00B0C'.format(
        int.from_bytes(read_value(), byteorder='little', signed=True)/100))
    # Create peripheral
    cpu_monitor = peripheral.Peripheral(adapter_address,
                                        local_name='CPU Monitor',
                                        appearance=1344)
    # Add service
    cpu_monitor.add_service(srv_id=1, uuid=CPU_TMP_SRVC, primary=True)
    # Add characteristic
    cpu_monitor.add_characteristic(srv_id=1, chr_id=1, uuid=CPU_TMP_CHRC,
                                   value=[], notifying=False,
                                   flags=['read', 'notify'],
                                   read_callback=read_value,
                                   write_callback=None,
                                   notify_callback=notify_callback
                                   )
    # Add descriptor
    cpu_monitor.add_descriptor(srv_id=1, chr_id=1, dsc_id=1, uuid=CPU_FMT_DSCP,
                               value=[0x0E, 0xFE, 0x2F, 0x27, 0x01, 0x00,
                                      0x00],
                               flags=['read'])
    # Publish peripheral and start event loop
    cpu_monitor.publish()


if __name__ == '__main__':
    # Get the default adapter address and pass it to main
    main(list(adapter.Adapter.available())[0].address)
