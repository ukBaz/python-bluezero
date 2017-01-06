from bluezero import microbit


def light_follow(bot, speed):
    while True:
        if bot.read_left_light() > 150:
            lmotor = speed
        else:
            lmotor = 0
        if bot.read_right_light() > 150:
            rmotor = speed
        else:
            rmotor = 0
        bot.drive(lmotor, rmotor)


if __name__ == '__main__':
    print('Scanning')
    bitbot = microbit.BitBot('micro:bit')
    print('Connecting')
    bitbot.connect()
    print('Connected!!')
    try:
        print('Light follow...')
        light_follow(bitbot, 80)
    except:
        print('Exception so stop')
        bitbot.stop()
        bitbot.disconnect()
    finally:
        print('Finally stop')
        bitbot.stop()
        bitbot.disconnect()
