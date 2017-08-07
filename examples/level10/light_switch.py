""""
This is an exercise to see what some Python would ideally look like
to extend a light switch to be switchable by both a switch and bluetooth.
An honourable mention to the Authors of Make:Bluetooth for the idea.
In particular Alasdair Allan that did a great demo at OSCON 2015.
"""
import logging
from gpiozero import LED
from gpiozero import Button

from bluezero import peripheral

logging.getLogger('bluezero.adapter').setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO)

# Hardware
# Ryanteck Traffic Hat
led = LED(24)
button = Button(25)
# pimoroni/explorer-hat
# led = LED(4)

led_state = False


def ble_state_callback():
    if switch_characteristic.value is None:
        print('Switch Characteristic is None')
        state_characteristic.send_notify_event(0)
        led.off()
    elif led.is_lit and switch_characteristic.value == 0:
        print('BLE send: off')
        state_characteristic.send_notify_event(0)
        led.off()
    elif led.is_lit is False and switch_characteristic.value == 1:
        print('BLE send: on')
        state_characteristic.send_notify_event(1)
        led.on()


def button_callback():
    print('Button Callback')
    if led.is_lit:
        print('Turning LED off')
        switch_characteristic.send_notify_event(0)
        state_characteristic.send_notify_event(0)
        led.off()
    else:
        print('Turning LED on')
        state_characteristic.send_notify_event(1)
        switch_characteristic.send_notify_event(1)
        led.on()


button.when_pressed = button_callback


# Bluetooth
# Service
light_service = peripheral.Service(
    '12341000-1234-1234-1234-123456789abc',
    True)

print('**light service', light_service)

# Swtich
switch_characteristic = peripheral.Characteristic(
    '12341001-1234-1234-1234-123456789abc',
    ['read', 'write'],
    light_service,
    value=0)
switch_characteristic.add_write_event(ble_state_callback)
# Descriptor
switch_descriptor = peripheral.UserDescriptor('Switch', switch_characteristic)
switch_characteristic.add_descriptor(switch_descriptor)

# Add characteristic
light_service.add_characteristic(switch_characteristic)

# state
state_characteristic = peripheral.Characteristic(
    '12341002-1234-1234-1234-123456789abc',
    ['notify'],
    light_service,
    value=0)
state_characteristic.add_notify_event(ble_state_callback)
state_characteristic.StartNotify()

# Descriptor
state_descriptor = peripheral.UserDescriptor('State', state_characteristic)
state_characteristic.add_descriptor(state_descriptor)

# Add characteristic
light_service.add_characteristic(state_characteristic)

for mngd_objcs in light_service.GetManagedObjects():
    print('Managed Objects: ', mngd_objcs)

# Add application [new in 5.38]
app = peripheral.Application('/org/bluez/hci0')
app.add_service(light_service)

app.add_device_name('BluezeroLight')

# Start service and advertise
try:
    app.start()
except KeyboardInterrupt:
    button.when_pressed = None
    print('KeyboardInterrupt')
finally:
    button.when_pressed = None
    app.stop()
    print('finally')
