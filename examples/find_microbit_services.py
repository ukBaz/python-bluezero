"""
Demo to show how to iterate around all BBC micro:bits that have already been
paired with (or previously connected to if pairing not required).
Connect to each one in turn and see what services are available on it.
Attempt to read the temperature and value of pin 4
"""
from bluezero import microbit


def main():
    for ubit_device in microbit.Microbit.available():
        ubit_device.connect()
        print(f'{ubit_device.name} device has the following services:')
        for service in ubit_device.services_available():
            print(f'\t[{ubit_device.address}] {service}')
        ubit_device.set_pin(4, pin_input=True, pin_analogue=False)
        print(f'\t\t[{ubit_device.address}] Temperature:',
              ubit_device.temperature)
        print(f'\t\t[{ubit_device.address}] Pin:', ubit_device.pin_values)

        ubit_device.disconnect()


if __name__ == '__main__':
    main()
