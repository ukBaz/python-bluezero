from bluezero.adapter import Adapter
from bluezero.device import Device
from bluezero.gatt import Client
from time import sleep

dongle = Adapter()
if dongle.powered() == 'off':
    print('Switching on dongle ({})'.format(dongle.name()))
    dongle.powered('on')
else:
    print('Dongle on: {}'.format(dongle.name()))

while dongle.powered() == 'off':
    sleep(1)
    print('Waiting for dongle to switch on')

batt = Device(dongle)

try:
    batt.request_device(name='Nexus', service='180f')
except Exception as e:
    print('{}'.format(e))
    exit()

sleep(2)
print('Adapter scanning: {}'.format(dongle.discovering()))
print('Returned device: {}'.format(batt.dev_addr))
print('Returned path: {}'.format(batt.dev_path))
print('Connected state: {}'.format(batt.connected()))
batt.connect(batt.dev_addr)
sleep(5)

if batt.connected():
    print('Successfully connect')
    gatt = Client(batt.dev_path)

if batt.connected():
    print('About to disconnect')
    batt.disconnect()
else:
    print('about to exit')

print('Connected stat: {}'.format(batt.connected()))

exit()
