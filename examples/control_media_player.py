# This script allows you to use your Linux computer as a Bluetooth speaker.
# The MediaPlayer interface lets you interact with the media player on the
# other end of the Bluetooth connection (e.g., the music player on your phone).
# It displays information about the current track.
# Before running this script, ensure you pair and connect your audio source.


from bluezero.adapter import list_adapters, Adapter
from bluezero import dbus_tools
from bluezero.device import Device
from bluezero import constants
from bluezero.media_player import MediaPlayer
import time


def filter_by_interface(objects, interface_name):
    """ filters the objects based on their support for the specified interface """
    object_paths = []
    for path in objects.keys():
        interfaces = objects[path]
        for interface in interfaces.keys():
            if interface == interface_name:
                object_paths.append(path)
    return object_paths


def filter_audio_devices(objects):
    """ Filters devices that support the A2DP audio profile (AudioSink) """
    audio_interface = 'org.freedesktop.DBus.Properties'  # Check this interface for supported profiles
    audio_devices = filter_by_interface(objects, audio_interface)

    audio_sink_devices = []
    for path in audio_devices:
        interfaces = objects[path]
        if 'org.freedesktop.DBus.Properties' in interfaces:
            if 'AudioSink' in interfaces['org.freedesktop.DBus.Properties']:
                audio_sink_devices.append(path)
    return audio_sink_devices


def ctrl_media_player(media_player):
    print("Make sure you are using a media player on your phone and "
          "have selected a track...")
    print("To interact with the Media Player, choose the corresponding number:")
    print("1. Play")
    print("2. Pause")
    print("3. Previous")
    print("4. Next")
    print("5. Track Info")
    print("6. End")

    while True:
        try:
            command = int(input("Enter a number (1-6): "))  # Get number input

            if command == 1:
                media_player.play()
            elif command == 2:
                media_player.pause()
            elif command == 3:
                media_player.previous()
            elif command == 4:
                media_player.next()
            elif command == 5:
                track_details = media_player.track
                time.sleep(2)
                for detail in track_details:
                    print(f'{detail} : {track_details[detail]}')
            elif command == 6:
                print("Ending media control.")
                break
            else:
                print("Invalid choice. Please select a number between 1 and 6.")

        except ValueError:
            print("Invalid input. Please enter a number between 1 and 6.")


def discover_devices(adapter_address):
    """ Function to discover nearby devices and list them """
    bluetooth_adapter = Adapter(adapter_address)
    bluetooth_adapter.nearby_discovery()
    print("Scanning for nearby devices...")

    # Find managed devices and their addresses
    dev_obj_path_list = filter_by_interface(dbus_tools.get_managed_objects(),
                                            constants.DEVICE_INTERFACE)
    dev_addr_list = list(map(dbus_tools.get_mac_addr_from_dbus_path, dev_obj_path_list))

    devices = []
    for addr in dev_addr_list:
        # Get the name of the device
        device = Device(adapter_address, addr)
        try:
            name = device.name
            devices.append((name, addr))
        except Exception as e:
            # If there is an error retrieving the device name, skip it
            print(f"Error retrieving name for device {addr}: {e}")

    return devices


def connect_to_device(adapter_address, device_address, retries=3, delay=5):
    """ Function to connect to the selected device with retries """
    attempt = 0
    while attempt < retries:
        try:
            remote_device = Device(adapter_address, device_address)

            # Verify if the device is paired, if not, pair it
            if remote_device.paired != 1:
                print(f"Pairing with {device_address}...")
                try:
                    remote_device.pair()  # Attempt to pair without timeout argument
                    print(f"Successfully paired with {device_address}")
                except Exception as e:
                    print(f"Pairing failed: {e}. Retrying... ({attempt + 1}/{retries})")
                    print("Make sure you confirm pairing on computer and phone")
                    attempt += 1
                    time.sleep(delay)
                    continue

            # Verify if the device is connected, if not, connect it
            if remote_device.connected != 1:
                print(f"Connecting to {device_address}...")
                remote_device.connect()

            # Wait for the media player to be ready
            time.sleep(10)

            # Initialize the media player and control it
            mp = MediaPlayer(device_address)
            ctrl_media_player(mp)
            return  # Successful connection

        except ValueError as e:
            print(f"Error: {e}. Retrying... ({attempt + 1}/{retries})")
            attempt += 1
            time.sleep(delay)

    print(f"Failed to connect to {device_address} after {retries} attempts.")


def select_adapter():
    """ Prompt user to select a Bluetooth adapter """
    adapters = list_adapters()
    if not adapters:
        print("No Bluetooth adapters found.")
        return None

    print("Available Bluetooth adapters:")
    for i, adapter in enumerate(adapters, 1):
        print(f"{i}. {adapter}")

    try:
        choice = int(input("Select the adapter by number: "))
        if 1 <= choice <= len(adapters):
            return adapters[choice - 1]
        else:
            print("Invalid choice. Please select a valid adapter.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None


if __name__ == '__main__':
    """ This script assumes that your remote device has its Bluetooth function on.
    It will list the nearby devices and let the user choose which one to connect to. """

    adapter_address = select_adapter()  # Select a Bluetooth adapter

    if not adapter_address:
        print("Exiting due to invalid adapter selection.")
        exit(1)

    while True:
        # Discover nearby devices
        devices = discover_devices(adapter_address)

        if devices:
            print("Nearby devices:")
            for i, (name, addr) in enumerate(devices, 1):
                print(f"{i}. {name} ({addr})")

            # Ask the user to select a device
            try:
                choice = int(input("Enter the number of the device you want to connect to "
                                   "(or 0 to refresh): "))
                if choice == 0:
                    continue  # Refresh discovery if the user selects 0
                selected_device = devices[choice - 1]  # Subtract 1 to match list index
                print(f"Attempting to connect to {selected_device[0]} "
                      f"({selected_device[1]})...")
                connect_to_device(adapter_address, selected_device[1])
                break  # Exit the loop after successful connection
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a valid device number.")
        else:
            print("No nearby devices found.")

        # Ask if the user wants to refresh discovery or exit
        refresh = input("Do you want to refresh device discovery? (y/n): ").strip().lower()
        if refresh != 'y':
            break