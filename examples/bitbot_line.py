from bluezero import microbit
from bluezero import tools


def left_line_cb(iface, changed_props, invalidated_props):
    if 'Value' in changed_props:
        print(changed_props['Value'][0], int(changed_props['Value'][0]))
        if changed_props['Value'][0] > 0:
            bitbot._left_motor(250)
        else:
            bitbot._left_motor(0)


def right_line_cb(iface, changed_props, invalidated_props):
    if 'Value' in changed_props:
        if changed_props['Value'][0] > 0:
            bitbot._right_motor(250)
        else:
            bitbot._right_motor(0)


def line_follow(bot, speed):
    while True:
        lline, rline = bot.read_lines()
        if not lline and rline:
            bot.drive(0, speed)
        elif lline and not rline:
            bot.drive(speed, 0)
        else:
            bot.drive(speed, speed)


print('Scanning')
bitbot = microbit.BitBot('micro:bit')
print('Connecting')
bitbot.connect()
print('Connected!!')

bitbot.subscribe_button_b(left_line_cb)
bitbot.subscribe_button_a(right_line_cb)

tools.start_mainloop()
print('pass mainloop')

if __name__ == '__main__':

    try:
        print('Line follow...')
        line_follow(bitbot, 18)
    except:
        print('Exception so stop')
        bitbot.stop()
        bitbot.disconnect()
    finally:
        print('Finally stop')
        bitbot.stop()
        bitbot.disconnect()
