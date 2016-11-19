import time
from bluezero import microbit

ubit = microbit.Microbit(name='puteg')

ubit.connect()

delay = ubit.display_scroll_delay()
ubit.display_text('Scroll speed {}'.format(delay))
time.sleep(10)
ubit.display_scroll_delay(0xBA)
ubit.display_text('This is a really long string ')
time.sleep(10)
while ubit.read_button_a() < 1:
    ubit.display_pixels(0b00000,
                        0b01000,
                        0b11111,
                        0b01000,
                        0b00000)
    time.sleep(0.5)
    ubit.display_clear()

while ubit.read_button_b() < 1:
    ubit.display_pixels(0b00000,
                        0b00010,
                        0b11111,
                        0b00010,
                        0b00000)
    time.sleep(0.5)
    ubit.display_clear()


ubit.disconnect()
