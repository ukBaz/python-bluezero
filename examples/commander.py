from bluezero import microbit
from time import sleep

stay_connected = True

cmdr = microbit.BitCommander(adapter_addr='B8:27:EB:22:57:E0',
                             device_addr='E3:AC:D2:F8:EB:B9')

cmdr.connect()
io_pin = cmdr.ubit._io_pin_config.value
ad_pin = cmdr.ubit._io_ad_config.value
print('Pin IO config {0:08b} {1:08b} {2:08b} {3:08b}'.format(io_pin[0],
                                                             io_pin[1],
                                                             io_pin[2],
                                                             io_pin[3]))
print('Pin AD config {0:08b} {1:08b} {2:08b} {3:08b}'.format(ad_pin[0],
                                                             ad_pin[1],
                                                             ad_pin[2],
                                                             ad_pin[3]))

while stay_connected:
    print(cmdr.dial, cmdr.joystick[0], cmdr.joystick[1], cmdr.joystick[2])
    print(cmdr.button_a, cmdr.button_b, cmdr.button_c, cmdr.button_d)
    if cmdr.button_a > 0:
        stay_connected = False
    sleep(0.25)

cmdr.disconnect()
print('Bye, bye!')
