import time
from bluezero import microbit


def main():
    ubit = microbit.Microbit(adapter_addr='00:01:02:03:04:05',
                             device_addr='E9:06:4D:45:FC:8D')

    ubit.connect()

    assert ubit.pixels == [0b01110,
                           0b10000,
                           0b10000,
                           0b10000,
                           0b01110]

    ubit.scroll_delay = 40
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


if __name__ == '__main__':
    main()
