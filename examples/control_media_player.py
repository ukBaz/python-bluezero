#  When using your Linux computer as a Bluetooth speaker the MediaPlayer
#  interfaces allows you interact with the media player on the other end of
#  the Bluetooth connection.
#  e.g. the music player on your phone.
#  This script displays information about the current track.
#  Before you can run this scrip you have to pair and connect your audio
#  source. For simplicity we can do this on the command line with the
#  bluetoothctl tool
#     pi@RPi3:~ $ bluetoothctl
#     [bluetooth]# agent NoInputNoOutput
#     Agent registered
#     [bluetooth]# discoverable on
#     Changing discoverable on succeeded
#     [CHG] Controller B8:27:EB:22:57:E0 Discoverable: yes
#
#  Now we have made the Raspberry Pi discoverable we can pair to it from the
#  mobile phone. Once it has paired you can tell the Raspberry Pi that it is a
#  trusted device
#
#     [Nexus 5X]# trust 64:BC:0C:F6:22:F8
#
#  Now the phone is connected you can run this script to find which track is
#  playing
#
#     pi@RPi3:~ $ python3 examples/control_media_player.py

from bluezero import dbus_tools
from bluezero import media_player

# Find the mac address of the first media player connected over Bluetooth
mac_addr = None
for dbus_path in dbus_tools.get_managed_objects():
    if dbus_path.endswith('player0'):
        mac_addr = dbus_tools.get_device_address_from_dbus_path(dbus_path)

if mac_addr:
    mp = media_player.MediaPlayer(mac_addr)

    track_details = mp.track
    for detail in track_details:
        print(f'{detail} : {track_details[detail]}')
else:
    print('Error: No media player connected')
