from bluezero import microbit
from bluezero import async_tools

ubit = microbit.Microbit(adapter_addr='02:00:AA:48:25:29',
                         device_addr='F1:55:90:65:29:DC',
                         accelerometer_service=False,
                         button_service=False,
                         led_service=False,
                         magnetometer_service=False,
                         pin_service=False,
                         temperature_service=False,
                         uart_service=True)
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
