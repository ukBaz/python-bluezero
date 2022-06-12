"""Example of how to create a Central device/GATT Client"""
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

    # Check bits field
    if value[0] & 0x01:
        # 16 bit heartrate value
        hr = value[1] << 8 | value[2]
    else:
        # 8 bit heartrate value
        hr = value[1]

    print("Notified of a heartrate of %d" % (hr))


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
    print("The location of the heart rate sensor is: %d" %
          int(location_char.value[0]))

    # Write the Control Point Value
    control_point_char.value = 1

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
