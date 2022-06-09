"""Example of how to create a Peripheral device/GATT Server"""
# Standard modules
import logging
import struct

# Bluezero modules
from bluezero import async_tools
from bluezero import adapter
from bluezero import peripheral

HRM_SRV = '0000180D-0000-1000-8000-00805f9b34fb'
HR_MSRMT_UUID =      '00002a37-0000-1000-8000-00805f9b34fb'
BODY_SNSR_LOC_UUID = '00002a38-0000-1000-8000-00805f9b34fb'
HR_CTRL_PT_UUID =    '00002a39-0000-1000-8000-00805f9b34fb'


heartrate = 60
def read_heartrate():
    global heartrate
    """
    Example read callback. Value returned needs to a list of bytes/integers
    in little endian format.

    // Send one byte of flags
    // As well as an 8 bit measurement

    :return: list of uint8 values
    """
    flags = 0b00000110
    heartrate = heartrate + 1
    print("Sending heartrate value of %d" % (heartrate))
    if heartrate > 180:
        heart_rate = 60
    return struct.pack('<BB', flags, heartrate)

def read_sensor_location():
    # Static 1 is Chest location
    # Little endian, unsigned char
    sensor_location = 1
    print("Sending sensor location of %d" % (sensor_location))
    return struct.pack('<B', sensor_location)

def update_value(characteristic):
    """
    Example of callback to send notifications

    :param characteristic:
    :return: boolean to indicate if timer should continue
    """
    # read/calculate new value.
    new_value = read_heartrate()
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
        async_tools.add_timer_seconds(1, update_value, characteristic)

def write_control_point(value, options):
    control_point = struct.unpack('<B', bytes(value))[0]
    print("Recieved control point value of: %d" % (control_point))

def main(adapter_address):
    """Creation of peripheral"""
    logger = logging.getLogger('localGATT')
    logger.setLevel(logging.DEBUG)

    # Create peripheral
    hr_monitor = peripheral.Peripheral(adapter_address,
                                        local_name='Heartrate Monitor',
                                        appearance=0x0340)
    # Add service
    hr_monitor.add_service(srv_id=1, uuid=HRM_SRV, primary=True)

    # Add characteristics
    hr_monitor.add_characteristic(srv_id=1, chr_id=1, uuid=HR_MSRMT_UUID,
                                   value=[], notifying=False,
                                   flags=['read', 'notify'], # May not exactly match standard, but including read for tutorial
                                   read_callback=read_heartrate,
                                   write_callback=None,
                                   notify_callback=notify_callback
                                   )

    hr_monitor.add_characteristic(srv_id=1, chr_id=2, uuid=BODY_SNSR_LOC_UUID,
                                   value=[], notifying=False,
                                   flags=['read'],
                                   read_callback=read_sensor_location,
                                   write_callback=None,
                                   notify_callback=None
                                   )

    hr_monitor.add_characteristic(srv_id=1, chr_id=3, uuid=HR_CTRL_PT_UUID,
                                   value=[], notifying=False,
                                   flags=['write'],
                                   read_callback=None,
                                   write_callback=write_control_point,
                                   notify_callback=None
                                   )

    # Publish peripheral and start event loop
    hr_monitor.publish()


if __name__ == '__main__':
    # Get the default adapter address and pass it to main
    main(list(adapter.Adapter.available())[0].address)