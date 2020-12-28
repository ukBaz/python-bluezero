from bluezero import microbit
from bluezero import async_tools

ubit = microbit.Microbit(adapter_addr='02:00:AA:48:25:29',
                         device_addr='F1:55:90:65:29:DC')
eloop = async_tools.EventLoop()
ubit.connect()


def ping():
    ubit.uart = 'ping#'
    return True


def goodbye():
    ubit.quit_async()
    ubit.disconnect()
    return False


ubit.subscribe_uart(print)
eloop.add_timer(10000, ping)
eloop.add_timer(30000, goodbye)

ubit.run_async()
