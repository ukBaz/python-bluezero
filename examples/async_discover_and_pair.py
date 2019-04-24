from bluezero import adapter
from bluezero import device
from bluezero import async_tools
from bluezero import constants


def start_disco():
    print('Starting scan')
    dongle.start_discovery()
    return False


def new_device_handler(device_path, device_info):
    print('Device path', device_path)
    if constants.DEVICE_INTERFACE in device_info:
        if 'micro:bit' in device_info[constants.DEVICE_INTERFACE]['Alias']:
            print('micro:bit found')
            dongle.stop_discovery()
            new_dev = device.Device(adapter_addr=dongle.address,
                                    device_addr=device_info[constants.DEVICE_INTERFACE]['Address'])
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

dongle.on_device_found = new_device_handler

eloop.add_timer(500, start_disco)
eloop.add_timer(30000, exit_test)

eloop.run()
