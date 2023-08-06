import random
import struct

from bluezero import adapter
from bluezero import dbus_tools
from bluezero import device
from bluezero import peripheral


SERVICE_UUID = "00001111-1234-1234-1234-123456789abc"
OPT_CHR_UUID = "00002222-1234-1234-1234-123456789abc"
NON_OPT_UUID = "00003333-1234-1234-1234-123456789abc"


def on_connect(ble_device: device.Device):
    print("Connected to " + str(ble_device.address))


def on_disconnect(adapter_address, device_address):
    print("Disconnected from " + device_address)


def get_address(options):
    dev_addr = dbus_tools.get_adapter_address_from_dbus_path(
        options.get('device'))
    return dbus_tools.dbus_to_python(dev_addr)


call_count: dict[str, int] = {}


def cb_with_options(options):
    """
    Callback with passing options - uses device address from options to keep a
    running counter of the number of times it was called, and return the count
    as LE 2-byte int
    """
    print(f"\nCalling with options: {options}")
    addr = get_address(options)
    count = call_count.setdefault(addr, 0)
    count += 1
    call_count[addr] = count
    print(f"\tReturning: {count}")
    print(f"\tAll counts are: {call_count}")
    return struct.pack("<h", count)


def cb_no_options():
    """
    Callback without options - just return a random number as an LE 2-byte int
    """
    print("\nCalling without options")
    num = random.randint(0, 1000)
    print(f"\tReturning: {num}")
    return struct.pack("<h", num)


def main(adapter_address):
    ble = peripheral.Peripheral(
        adapter_address,
        local_name="Options Callback Test")
    ble.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)

    ble.add_characteristic(
        srv_id=1,
        chr_id=1,
        uuid=OPT_CHR_UUID,
        value=[],
        notifying=False,
        flags=["read"],
        read_callback=cb_with_options,
    )

    ble.add_characteristic(
        srv_id=1,
        chr_id=2,
        uuid=NON_OPT_UUID,
        value=[],
        notifying=False,
        flags=["read"],
        read_callback=cb_no_options,
    )
    ble.on_connect = on_connect
    ble.on_disconnect = on_disconnect
    ble.publish()


if __name__ == "__main__":
    dongle = list(adapter.Adapter.available())[0].address
    main(dongle)
