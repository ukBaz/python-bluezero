""""
This is an exercise to see what some Python would ideally look like
to extend a light switch to be switchable by both a switch and bluetooth.
An honourable mention to the Authors of Make:Bluetooth for the idea.
In particular Alasdair Allan that did a great demo at OSCON 2015.
"""
import sys
import os

from gpiozero import LED
from gpiozero import Button

sys.path.insert(0,
                os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])
from bluezero import peripheral

import array

# Hardware
# Ryanteck Traffic Hat
led = LED(24)
button = Button(25)
# pimoroni/explorer-hat
# led = LED(4)


def ble_state_callback():
    print('State Callback', led.is_lit, switch_characteristic.value)
    if state_characteristic.value is None:
        print('Switch Characteristic is None')
        led.off()
    elif led.is_lit is True:
        print('BLE send: off')
        state_characteristic.send_notify_event(0)
        led.off()
    elif led.is_lit is False:
        print('BLE send: on')
        state_characteristic.send_notify_event(1)
        led.on()


def button_callback():
    print('Button Callback')
    if led.is_lit:
        print('Turning LED off')
        state_characteristic.send_notify_event(0)
        led.off()
    else:
        print('Turning LED on')
        state_characteristic.send_notify_event(1)
        led.on()


button.when_pressed = button_callback


# Bluetooth
# Service
light_service = peripheral.Service(
    '12341000-1234-1234-1234-123456789abc',
    True)

print('**light service', light_service)

# state
state_characteristic = peripheral.Characteristic(
    '12341002-1234-1234-1234-123456789abc',
    ['read', 'write', 'notify'],
    light_service)
state_characteristic.add_notify_event(ble_state_callback)
state_characteristic.add_write_event(button_callback)

# Descriptor
state_descriptor = peripheral.UserDescriptor('State', state_characteristic)
state_characteristic.add_descriptor(state_descriptor)

# Add characteristic
light_service.add_characteristic(state_characteristic)

for mngd_objcs in light_service.GetManagedObjects():
    print('Managed Objects: ', mngd_objcs)

# Add application [new in 5.38]
app = peripheral.Application()
app.add_service(light_service)

# Start service and advertise
try:
    app.start()
except KeyboardInterrupt:
    button.when_pressed = None
    print('KeyboardInterrupt')
finally:
    button.when_pressed = None
    print('finally')
