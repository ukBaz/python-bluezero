import time
from bluezero import microbit

ubit = microbit.Microbit(name='puteg')

ubit.connect()

ubit.display_text('Test string')
ubit.display_text('This is a really long string and will get truncated which is good?')

while ubit.connected:
    print(ubit.read_button_a())
    time.sleep(0.5)


ubit.display_text()
