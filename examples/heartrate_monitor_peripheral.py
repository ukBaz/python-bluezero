"""Example of how to create a Peripheral device/GATT Server"""
# Standard modules
from enum import IntEnum
import logging
import struct

# Bluezero modules
from bluezero import async_tools
from bluezero import adapter
from bluezero import peripheral

# Documentation can be found on Bluetooth.com
# https://www.bluetooth.com/specifications/specs/heart-rate-service-1-0/

# There are also published xml specifications for possible values
# For the Service:
# https://github.com/oesmith/gatt-xml/blob/master/org.bluetooth.service.heart_rate.xml

# For the Characteristics:
# Heart Rate Measurement
# https://github.com/oesmith/gatt-xml/blob/master/org.bluetooth.characteristic.heart_rate_measurement.xml
# Body Sensor Location
# https://github.com/oesmith/gatt-xml/blob/master/org.bluetooth.characteristic.body_sensor_location.xml
# Heart Rate Control Point
# https://github.com/oesmith/gatt-xml/blob/master/org.bluetooth.characteristic.heart_rate_control_point.xml


HRM_SRV = '0000180D-0000-1000-8000-00805f9b34fb'
HR_MSRMT_UUID = '00002a37-0000-1000-8000-00805f9b34fb'
BODY_SNSR_LOC_UUID = '00002a38-0000-1000-8000-00805f9b34fb'
HR_CTRL_PT_UUID = '00002a39-0000-1000-8000-00805f9b34fb'


class HeartRateMeasurementFlags(IntEnum):
    HEART_RATE_VALUE_FORMAT_UINT16 = 0b00000001
    SENSOR_CONTACT_DETECTED = 0b00000010
    SENSOR_CONTACT_SUPPORTED = 0b00000100
    ENERGY_EXPENDED_PRESENT = 0b00001000
    RR_INTERVALS_PRESENT = 0b00010000


class BodySensorLocation(IntEnum):
    OTHER = 0
    CHEST = 1
    WRIST = 2
    FINGER = 3
    HAND = 4
    EAR_LOBE = 5
    FOOT = 6


class HeartRateControlPoint(IntEnum):
    RESET_ENERGY_EXPENDED = 1


# Heartrate measurement and energy expended is persistent between function
# reads
heartrate = 60
energy_expended = 0


def read_heartrate():
    """
    Generates new heartrate and energy expended measurements
    Increments heartrate and energy_expended variables and serializes
    them for BLE transport.
    :return: bytes object for Heartrate Measurement Characteristic
    """
    global heartrate, energy_expended
    # Setup flags for what's supported by this example
    # We are sending UINT8 formats, so don't indicate
    # HEART_RATE_VALUE_FORMAT_UINT16
    flags = HeartRateMeasurementFlags.SENSOR_CONTACT_DETECTED | \
        HeartRateMeasurementFlags.SENSOR_CONTACT_SUPPORTED | \
        HeartRateMeasurementFlags.ENERGY_EXPENDED_PRESENT

    # Increment heartrate by one each measurement cycle
    heartrate = heartrate + 1
    if heartrate > 180:
        heartrate = 60

    # Increment energy expended each measurement cycle
    energy_expended = energy_expended + 1

    print(
        f"Sending heartrate value of {heartrate} \
        and energy expended of {energy_expended} kJ")
    return struct.pack('<BBH', flags, heartrate, energy_expended)


def read_sensor_location():
    """
    Reports the simulated heartrate sensor location.
    :return: bytes object for Body Sensor Location Characteristic
    """
    sensor_location = BodySensorLocation.CHEST
    print(f"Sending sensor location of {sensor_location!r}")
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
    which calls the update callback every 2 seconds

    :param notifying: boolean for start or stop of notifications
    :param characteristic: The python object for this characteristic
    """
    if notifying:
        async_tools.add_timer_seconds(1, update_value, characteristic)


def write_control_point(value, options):
    """
    Called when a central writes to our write characteristic.

    :param value: data sent by the central
    :param options:
    """
    global energy_expended

    # Note use of control_point, to assign one or more values into variables
    # from struct.unpack output which returns a tuple
    control_point, = struct.unpack('<B', bytes(value))
    if control_point == HeartRateControlPoint.RESET_ENERGY_EXPENDED:
        print("Resetting Energy Expended from Sensor Control Point Request")
        energy_expended = 0


def main(adapter_address):
    """
    Creates advertises and starts the peripheral

    :param adapter_address: the MAC address of the hardware adapter
    """
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
                                  # May not exactly match standard, but
                                  # including read for tutorial
                                  flags=['read', 'notify'],
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
