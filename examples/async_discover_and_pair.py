from bluezero import adapter
from bluezero import device
from bluezero import async_tools
from bluezero import constants
from bluezero import microbit
from gi.repository import GLib
from time import sleep

ubit_device = None

def start_disco():
    print('Starting scan')
    dongle.start_discovery()
    return False


def device_found_handler(device_obj):
    if 'micro:bit' in device_obj.alias:
        print('micro:bit found')
        dongle.stop_discovery()
        device_obj.pair()
        waiting = True
        while waiting:
            print('waiting...')
            sleep(1)
            print('Status ubit', device_obj.connected, 
                                 device_obj.services_resolved, 
                                 device_obj.paired)
            waiting = not device_obj.paired
        if device_obj.paired:
            print('Dongle Addres', dongle.address, device_obj.address)
            ubit_device = microbit.Microbit(adapter_addr=dongle.address,
                                 device_addr=device_obj.address,
                                 accelerometer_service=False,
                                 button_service=True,
                                 led_service=False,
                                 magnetometer_service=False,
                                 pin_service=False,
                                 temperature_service=False)
            print(dir(ubit_device))
            # Need long sleep here to allow micro:bit to switch from pairing mode
            # to normal mode. There should be a smarter way to do this I just can't
            # think what it is right now
            sleep(30)
            print('call ubit', ubit_device.connected, ubit_device.ubit.services_resolved)
            # Using native GLib timeout method because Bluezero one does not take parameters
            # Should update the async_tools.add_timer method to accept them
            GLib.timeout_add(500, connect_ubit, ubit_device)
    return True


def connect_ubit(new_device):
    print('New Device', new_device)
    print('ubit Device', ubit_device)
    new_device.connect()
    print('Add button A')
    new_device.subscribe_button_a(btn_a_action)
    print('Add button B')
    new_device.subscribe_button_b(btn_a_action)
    False

def btn_a_action(*args, **kwargs):
    # Need to update micro:bit class so the user callback
    # has one parameter which is the button value as an integer
    print('button a')
    print('args = ', args)
    print('kwargs = ', kwargs)

def btn_b_action(*args, **kwargs):
    print('button b')
    print('args = ', args)
    print('kwargs = ', kwargs)

def exit_test():
    print('Times up!')
    if dongle.discovering:
        dongle.stop_discovery()
    eloop.quit()
    return False


dongle = adapter.Adapter()
eloop = async_tools.EventLoop()

dongle.on_device_found = device_found_handler

eloop.add_timer(500, start_disco)
eloop.add_timer(300000, exit_test)

eloop.run()
