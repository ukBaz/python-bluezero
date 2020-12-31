import sys
from bluezero import adapter
from bluezero import microbit
from bluezero import async_tools


def main(adapter_addrss, device_address):
    ubit = microbit.Microbit(adapter_addr=adapter_addrss,
                             device_addr=device_address)

    def goodbye(data):
        print(data)
        ubit.quit_async()
        ubit.disconnect()
        return True

    ubit.connect()
    ubit.subscribe_uart(goodbye)
    ubit.uart = 'Ping#'

    ubit.run_async()


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 3:
        main(args[1], args[2])
    else:
        print('Needs to be called with Adapter Address and micro:bit address')
        print('Suggestions:')
        for dongle in adapter.Adapter.available():
            for mbit in microbit.Microbit.available(dongle.address):
                print(f'\tpython3 {sys.argv[0]} '
                      f'{dongle.address} {mbit.address}')
