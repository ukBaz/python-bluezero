import time
from bluezero import microbit

ubit = microbit.Microbit(name='puteg')

ubit.connect()

assert ubit.read_pixels() == ['0b1110',
                              '0b10000',
                              '0b10000',
                              '0b10000',
                              '0b1110']

ubit.play_beep(0.25)
ubit.display_scroll_delay(20)
delay = ubit.display_scroll_delay()
ubit.display_text('Scroll speed {}'.format(delay))
time.sleep(5)
ubit.display_text('This is a really long string ')
time.sleep(5)

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


ubit.display_clear()
ubit.display_scroll_delay(120)
ubit.display_text('{0}'.format(ubit.read_temperature()))
time.sleep(5)

ubit.display_text('{0}'.format(ubit.read_accelerometer()))
time.sleep(5)

ubit.disconnect()
