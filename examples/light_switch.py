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

# Hardware
led = LED(24)
button = Button(25)
LED_on = False


def ble_switch_callback():
    print('Call-back', led.is_lit, switch_characteristic.ReadValue())
    if switch_characteristic.ReadValue() is None:
        print('Switch Characteristic is None')
        switch_characteristic.WriteValue(0)
    elif led.is_lit is True and switch_characteristic.ReadValue() == 0:
        print('BLE send: off')
        state_characteristic.WriteValue(0)
        led.off()
    elif led.is_lit is False and switch_characteristic.ReadValue() == 1:
        print('BLE send: on')
        state_characteristic.WriteValue(1)
        led.on()


def button_callback():
    if led.is_lit:
        switch_characteristic.WriteValue(0)
        state_characteristic.WriteValue(0)
        switch_characteristic.send_notify_event(0)
        led.off()
    else:
        switch_characteristic.WriteValue(1)
        state_characteristic.WriteValue(1)
        switch_characteristic.send_notify_event(1)
        led.on()


button.when_pressed = button_callback


# Bluetooth
# Service
light_service = peripheral.Service(
    '12341000-1234-1234-1234-123456789abc',
    True)

print('**light service', light_service)

# switch
switch_characteristic = peripheral.Characteristic(
    '12341001-1234-1234-1234-123456789abc',
    ['read', 'write'],
    light_service)
switch_characteristic.add_notify_event(ble_switch_callback)
switch_characteristic.StartNotify()
switch_descriptor = peripheral.UserDescriptor('Switch', switch_characteristic)
switch_characteristic.add_descriptor(switch_descriptor)
light_service.add_characteristic(switch_characteristic)
print('**Path: ', light_service.get_characteristics())

# state
state_characteristic = peripheral.Characteristic(
    '12341002-1234-1234-1234-123456789abc',
    ['notify'],
    light_service)
state_descriptor = peripheral.UserDescriptor('State', state_characteristic)
state_characteristic.add_descriptor(switch_descriptor)
light_service.add_characteristic(state_characteristic)

# Debug code
light_service.get_properties()
light_service.get_path()
light_service.get_characteristic_paths()
light_service.get_characteristics()
print('\nlight_service GetAll:\n',
      light_service.GetAll('org.bluez.GattService1'))
print('\nGet Managed Objects:\n',
      light_service.GetManagedObjects())
print('\nGet Properties:\n',
      light_service.get_characteristics()[0].get_properties())

switch_characteristic.get_properties()
# Start service and advertise
try:
    light_service.start()
except KeyboardInterrupt:
    button.when_pressed = None
    print('KeyboardInterrupt')
finally:
    button.when_pressed = None
    print('finally')
