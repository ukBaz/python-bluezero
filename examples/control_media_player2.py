from bluezero.adapter import list_adapters, Adapter
from bluezero import dbus_tools
from bluezero.device import Device
from bluezero import constants
from bluezero.media_player import MediaPlayer
import time


def filter_by_interface(objects, interface_name):
    """ filters the objects based on their support
        for the specified interface """
    object_paths = []
    for path in objects.keys():
        interfaces = objects[path]
        for interface in interfaces.keys():
            if interface == interface_name:
                object_paths.append(path)
    return object_paths


def ctrl_media_player(media_player):
    print("Make sure you are using a media player on your phone and "
          "have selected a track...")
    print("To interact with the Media Player you can type the following "
          "on the termminal standard input: ")
    print("play ,pause ,previous ,next ,previous ,infos and end")
    while (True):
        command = input()

        if command == "play":
            media_player.play()

        elif command == "previous":
            media_player.previous()

        elif command == "next":
            media_player.next()

        elif command == "pause":
            media_player.pause()

        elif command == "infos":
            track_details = media_player.track
            time.sleep(2)
            for detail in track_details:
                print(f'{detail} : {track_details[detail]}')

        elif command == "end":
            break

        else:
            print("this command is not recognized")


if __name__ == '__main__':
    """ This script considers that your remote device has its bluetooth
    function on. Since we know that get_managed_objects() methods does keep
    device objects found earlier in most situation we will use it
    to retrieve our targeted device adresse"""

    "Replace the mac address by the targeted device"
    target_dev_address = '94:87:E0:8A:3B:A1'

    adapter_adress = list_adapters()[0]
    bluetooth_adapter = Adapter(adapter_adress)
    bluetooth_adapter.nearby_discovery()

    "Find managed devices adresses"
    dev_obj_path_list = filter_by_interface(
        dbus_tools.get_managed_objects(),
        constants.DEVICE_INTERFACE)
    dev_addr_list = list(
        map(dbus_tools.get_mac_addr_from_dbus_path, dev_obj_path_list))
    print("Managed devices: ", dev_addr_list)

    "Attempt to connect pair and connect to the device"
    remote_device = None
    if target_dev_address in dev_addr_list:
        remote_device = Device(adapter_adress, target_dev_address)

        "Verify if the device has already been paired"
        if not remote_device.paired == 1:
            remote_device.pair()

        "Verify if the device has already been connected"
        if not remote_device.connected == 1:
            remote_device.connect()

        "Wait for the player to be ready to be used"
        time.sleep(10)
        mp = MediaPlayer(target_dev_address)
        ctrl_media_player(mp)
    else:
        print("Make sure that your device has been discovered")
