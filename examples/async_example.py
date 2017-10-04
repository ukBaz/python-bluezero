from bluezero import microbit

ubit = microbit.Microbit(adapter_addr='B8:27:EB:22:57:E0',
                         device_addr='E3:AC:D2:F8:EB:B9')


def button_callback(*args, **kwargs):
    print('Hello, World')
    print('args = ', args)
    print('kwargs = ', kwargs)


ubit.connect()

ubit.subscribe_button_a(button_callback)
print('About to launch')
ubit.run_async()
# mainloop.run()
print('We have crashed and burned')
