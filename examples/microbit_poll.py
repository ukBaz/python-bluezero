import time
from bluezero import microbit

ubit = microbit.Microbit(adapter_addr='B8:27:EB:22:57:E0',
                         device_addr='E3:AC:D2:F8:EB:B9')

ubit.connect()

assert ubit.pixels == [0b01110,
                       0b10000,
                       0b10000,
                       0b10000,
                       0b01110]

ubit.scroll_delay = 20
delay = ubit.scroll_delay
ubit.text = 'Scroll speed {}'.format(delay)
time.sleep(5)
ubit.text = 'This is a really long string '
time.sleep(5)

while not ubit.button_a:
    ubit.pixels = [0b00000,
                   0b01000,
                   0b11111,
                   0b01000,
                   0b00000]
    time.sleep(0.5)
    ubit.clear_display()

while not ubit.button_b:
    ubit.pixels = [0b00000,
                   0b00010,
                   0b11111,
                   0b00010,
                   0b00000]
    time.sleep(0.5)
    ubit.clear_display()

ubit.clear_display()
ubit.scroll_delay = 120
ubit.text = '{0}'.format(ubit.temperature)
time.sleep(5)

ubit.text = '{0}'.format(ubit.accelerometer)
time.sleep(5)

ubit.disconnect()
