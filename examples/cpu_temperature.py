# Standard modules
import logging
import os
import random
import dbus
from gi.repository import GLib

# Bluezero modules
from bluezero import async_tools
from bluezero import adapter
from bluezero import advertisement
from bluezero import constants
from bluezero import dbus_tools
from bluezero import localGATT
from bluezero import GATT
from bluezero import peripheral
from bluezero import tools

# constants
CPU_TMP_SRVC = '12341000-1234-1234-1234-123456789abc'
CPU_TMP_CHRC = '2A6E'
CPU_FMT_DSCP = '2904'


def read_value():
    """
    Mock reading CPU temperature callback. Return iterable of integer values.
    Bluetooth expects the values to be in little endian format

    :return: iterable of uint8 values
    """
    cpu_value = random.randrange(3200, 5310, 10) / 100
    return list(int(cpu_value * 100).to_bytes(2,
                                              byteorder='little', signed=True))


def update_value(characteristic):
    new_value = read_value()
    characteristic.Set(constants.GATT_CHRC_IFACE, 'Value', new_value)
    return characteristic.Get(constants.GATT_CHRC_IFACE, 'Notifying')


def notify_callback(notifying, characteristic):
    if notifying:
        async_tools.add_timer_seconds(2, update_value, characteristic)


def main(adapter_address, test_mode=False):
    logger = logging.getLogger('localGATT')
    logger.setLevel(logging.DEBUG)
    print('CPU temperature is {}C'.format(read_value()))
    cpu_monitor = peripheral.Peripheral(adapter_address,
                                        local_name='CPU Monitor',
                                        appearance=1344)
    cpu_monitor.add_service(1, CPU_TMP_SRVC, True)
    cpu_monitor.add_characteristic(1, 1, CPU_TMP_CHRC, [], False,
                                   ['read', 'notify'],
                                   read_callback=read_value,
                                   write_callback=None,
                                   notify_callback=notify_callback
                                   )
    cpu_monitor.publish()


if __name__ == '__main__':
    main(list(adapter.Adapter.available())[0].address)
