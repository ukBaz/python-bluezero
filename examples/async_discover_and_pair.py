from bluezero import adapter
from bluezero import device
from bluezero import async_tools
from bluezero import constants


def start_disco():
    print('Starting scan')
    dongle.start_discovery()
    return False


def device_found_handler(device_path, device_info):
    if 'micro:bit' in device_info['Alias']:
        print('micro:bit found')
        dongle.stop_discovery()
        new_dev = device.Device(adapter_addr=dongle.address,
                                device_addr=device_info['Address'])
        new_dev.pair()
    return True


def exit_test():
    print('Exiting eventloop')
    if dongle.discovering:
        dongle.stop_discovery()
    eloop.quit()
    return False


dongle = adapter.Adapter()
eloop = async_tools.EventLoop()

dongle.on_device_found = device_found_handler

eloop.add_timer(500, start_disco)
eloop.add_timer(30000, exit_test)

eloop.run()
