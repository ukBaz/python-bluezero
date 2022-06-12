"""Example of how to create a Central device/GATT Client"""
from enum import IntEnum
import struct

from bluezero import adapter
from bluezero import central

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


def scan_for_heartrate_monitors(
        adapter_address=None,
        hrm_address=None,
        timeout=5.0):
    # If there are multiple adapters on your system, this will scan using
    # all dongles unless an adapter is specified through its MAC address
    for dongle in adapter.Adapter.available():
        # Filter dongles by adapter_address if specified
        if adapter_address and adapter_address.upper() != dongle.address():
            continue

        # Actually listen to nearby advertisements for timeout seconds
        dongle.nearby_discovery(timeout=timeout)

        # Iterate through discovered devices
        for dev in central.Central.available(dongle.address):
            # Filter devices if we specified a HRM address
            if hrm_address and hrm_address == dev.address:
                yield dev

            # Otherwise, return devices that advertised the HRM Service UUID
            if HRM_SRV.lower() in dev.uuids:
                yield dev


def on_new_heart_rate_measurement(iface, changed_props, invalidated_props):
    value = changed_props.get('Value', None)
    if not value:
        return

    flags = value[0]
    payload = value[1:]

    # Setup a struct format based on flags
    fmt = '<'

    if flags & HeartRateMeasurementFlags.HEART_RATE_VALUE_FORMAT_UINT16:
        fmt += 'H'  # Add a UINT16 heart rate measurement
    else:
        fmt += 'B'  # Add a UINT8 heart rate measurement

    if flags & HeartRateMeasurementFlags.ENERGY_EXPENDED_PRESENT:
        fmt += 'H'  # Add a UINT16 energy expended measurement

    # RR_INTERVALS_PRESENT is not common and too complex for this toy example

    measurements = struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)]))

    hr = measurements[0]  # Guaranteed to be present
    print("Notified of a heartrate of %d beats per minute" % (hr))

    if flags & HeartRateMeasurementFlags.ENERGY_EXPENDED_PRESENT:
        energy_expended = measurements[1]
        print("Total Exercise Calories Burned: %d" % (energy_expended / 4.184))


def connect_and_run(dev=None, device_address=None):
    # Create Interface to Central
    if dev:
        monitor = central.Central(
            adapter_addr=dev.adapter,
            device_addr=dev.address)
    else:
        monitor = central.Central(device_addr=device_address)

    # Characteristics that we're interested must be added to the Central
    # before we connect so they automatically resolve BLE properties
    # Heart Rate Measurement - notify
    measurement_char = monitor.add_characteristic(HRM_SRV, HR_MSRMT_UUID)

    # Body Sensor Location - read
    location_char = monitor.add_characteristic(HRM_SRV, BODY_SNSR_LOC_UUID)

    # Heart Rate Control Point - write - not always supported
    control_point_char = monitor.add_characteristic(HRM_SRV, HR_CTRL_PT_UUID)

    # Now Connect to the Device
    if dev:
        print("Connecting to " + dev.alias)
    else:
        print("Connecting to " + device_address)

    monitor.connect()

    # Check if Connected Successfully
    if not monitor.connected:
        print("Didn't connect to device!")
        return

    # Example Usage!!!

    # Read the Body Sensor Location
    location = location_char.value
    if location:
        print("The location of the heart rate sensor is: %d" % int(location))

    # Write the Control Point Value to reset calories burned
    control_point_char.value = HeartRateControlPoint.RESET_ENERGY_EXPENDED

    # Enable heart rate notifications
    measurement_char.start_notify()
    measurement_char.add_characteristic_cb(on_new_heart_rate_measurement)

    try:
        # Startup in async mode to enable notify, etc
        monitor.run()
    except KeyboardInterrupt:
        print("Disconnecting")

    measurement_char.stop_notify()
    monitor.disconnect()


if __name__ == '__main__':
    # Discovery nearby heart rate monitors
    devices = scan_for_heartrate_monitors()
    for hrm in devices:
        print("Heart Rate Measurement Device Found!")

        # Connect to first available heartrate monitor
        connect_and_run(hrm)

        # Only demo the first device found
        break
