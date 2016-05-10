import sys
import os
sys.path.insert(0,
                os.path.split(
                    os.path.dirname(
                        os.path.realpath(__file__)))[0])

from time import sleep
from threading import Thread

from bluezero import peripheral

# Bluetooth Service

service1 = peripheral.Service('12341000-1234-1234-1234-123456789abc', True)
char1 = peripheral.Characteristic('12341002-1234-1234-1234-123456789abc',
                                  ['read', 'write', 'notify'],
                                  service1)
service1.add_characteristic(char1)

service2 = peripheral.Service('12341000-1234-1234-1234-123456789def', True)
char2 = peripheral.Characteristic('12341002-1234-1234-1234-123456789def',
                                  ['read', 'write', 'notify'],
                                  service2)
service2.add_characteristic(char2)


app1 = peripheral.Application()
app1.add_service(service1)

app2 = peripheral.Application()
app2.add_service(service2)

TOGGLE_DELAY = 30


def worker():
    try:
        print("Allowing the first app {} secs to run.".format(TOGGLE_DELAY))
        sleep(TOGGLE_DELAY)
        while True:
            print("App1 down, App2 up")
            app1.stop()
            app2.start()
            sleep(TOGGLE_DELAY)
            print("App1 up, App2 down")
            app1.start()
            app2.stop()
            sleep(TOGGLE_DELAY)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')


workerThread = Thread(target=worker)
workerThread.daemon = False
workerThread.start()

# Start service and advertise
app1.start()
