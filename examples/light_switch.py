""""
This is an exercise to see what some Python would ideally look like
to extend a light switch to be switchable by both a switch and bluetooth.
An honourable mention to the Authors of Make:Bluetooth for the idea.
In particular Alasdair Allan that did a great demo at OSCON 2015.
"""
from gpiozero import LED
from gpiozero import Button
import sys
import os
# sys.path.insert(0, '/home/pi/python/python-bluezero')
sys.path.insert(0, os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])
# print('Directory /home/pi/python/python-bluezero', os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])
from bluezero import peripheral
from signal import pause

# Hardware
led = LED(24)
button = Button(25)
LED_on = False

def ble_switch_callback():
    print('Call-back', led.is_lit, switch_characteristic.ReadValue())
    if switch_characteristic.ReadValue()[0] is None:
        print('Switch Characteristic is None')
        switch_characteristic.WriteValue(0)
    elif led.is_lit is True and int(switch_characteristic.ReadValue()) == 0:
        print('BLE send off')
        state_characteristic.WriteValue(0)
        led.off()
    elif led.is_lit is False and int(switch_characteristic.ReadValue()) == 1:
        print('BLE send on')
        state_characteristic.WriteValue(1)
        led.on()


def button_callback():
    if led.is_lit:
        switch_characteristic.WriteValue(0)
        state_characteristic.WriteValue(0)
        led.off()
    else:
        switch_characteristic.WriteValue(1)
        state_characteristic.WriteValue(1)
        led.on()


button.when_pressed = button_callback


# Bluetooth
# Service
light_service = peripheral.Service('12341000-1234-1234-1234-123456789abc', True)
print('**light service', light_service)

# switch
switch_characteristic = peripheral.Characteristic('12341001-1234-1234-1234-123456789abc',
                                                  ['read', 'write'],
                                                  light_service)
switch_characteristic.add_notify_event(ble_switch_callback)
switch_characteristic.StartNotify()
switch_descriptor = peripheral.UserDescriptor('Switch', switch_characteristic)
switch_characteristic.add_descriptor(switch_descriptor)
print('**Path: ', light_service.get_characteristics())
light_service.add_characteristic(switch_characteristic)

# state
state_characteristic = peripheral.Characteristic('12341002-1234-1234-1234-123456789abc',
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
light_service.GetAll('org.bluez.GattService1')
light_service.GetManagedObjects()

# Start service and advertise
light_service.start()

# pause()
