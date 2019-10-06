from bluezero import microbit

cmdr = microbit.BitCommander(adapter_addr='B8:27:EB:22:57:E0',
                             device_addr='E3:AC:D2:F8:EB:B9')


def button_callback(status):
    print('Button A status: ', status)


def pin_callback(pin, value):
    if pin == 12:
        if value:
            print('Red button')
    elif pin == 14:
        if value:
            print('Green button')
    elif pin == 15:
        if value:
            print('Blue button')
    elif pin == 16:
        if value:
            print('White button')
    elif pin == 2:
        print('Dial = {}'.format(value))
    elif pin == 1:
        if value < 150 or value > 170:
            print('x-axis = {}'.format(value))
    elif pin == 0:
        if value < 150 or value > 170:
            print('y-axis = {}'.format(value))


cmdr.connect()

cmdr.subscribe_pins(pin_callback)
cmdr.ubit.subscribe_button_a(button_callback)

print('About to launch')

cmdr.run_async()

print('We have crashed and burned')
