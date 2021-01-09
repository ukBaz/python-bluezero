"""Access BlueZ Media Player functionality"""
import dbus

# python-bluezero imports
from bluezero import constants
from bluezero import dbus_tools
from bluezero import tools

logger = tools.create_module_logger(__name__)


class MediaPlayerError(Exception):
    """Custom exception"""
    pass


def _find_player_path(device_address):
    """ finds the player_path corresponding to the device addr"""
    player_path_list = []
    mngd_objs = dbus_tools.get_managed_objects()
    for path in dbus_tools.get_managed_objects():
        if mngd_objs[path].get(constants.MEDIA_PLAYER_IFACE):
            player_path_list.append(path)

    for path in player_path_list:
        found_address = dbus_tools.get_device_address_from_dbus_path(path)
        if device_address == found_address:
            return path
    raise MediaPlayerError("No player found for the device")


class MediaPlayer:
    """Bluetooth MediaPlayer Class.
    This class instantiates an object that is able to interact with
    the player of a Bluetooth device and get audio from its source.
    """

    def __init__(self, device_addr):
        """Default initialiser.

        Creates the interface to the remote Bluetooth device.

        :param device_addr: Address of Bluetooth device player to use.
        """
        self.player_path = _find_player_path(device_addr)
        self.player_object = dbus_tools.get_dbus_obj(self.player_path)
        self.player_methods = dbus_tools.get_dbus_iface(
            constants.MEDIA_PLAYER_IFACE, self.player_object)
        self.player_props = dbus_tools.get_dbus_iface(
            dbus.PROPERTIES_IFACE, self.player_object)

    @property
    def browsable(self):
        """If present indicates the player can be browsed using MediaFolder
        interface."""
        return self.player_props.Get(
            constants.MEDIA_PLAYER_IFACE, 'Browsable')

    @property
    def searchable(self):
        """If present indicates the player can be searched using
        MediaFolder interface."""
        return self.player_props.Get(
            constants.MEDIA_PLAYER_IFACE, 'Searchable')

    @property
    def track(self):
        """Return a dict of the track metadata."""
        return self.player_props.Get(
            constants.MEDIA_PLAYER_IFACE, 'Track')

    @property
    def device(self):
        """Return Device object path"""
        return self.player_props.Get(
            constants.MEDIA_PLAYER_IFACE, 'Device')

    @property
    def playlist(self):
        """Return the Playlist object path."""
        return self.player_props.Get(
            constants.MEDIA_PLAYER_IFACE, 'Playlist')

    @property
    def equalizer(self):
        """Return the equalizer value."""
        return self.player_props.Get(
            constants.MEDIA_PLAYER_IFACE, 'Equalizer')

    @equalizer.setter
    def equalizer(self, value):
        """Possible values: "off" or "on"."""
        self.player_props.Set(
            constants.MEDIA_PLAYER_IFACE, 'Equalizer', value)

    @property
    def name(self):
        """Return the player name"""
        return self.player_props.Get(
            constants.MEDIA_PLAYER_IFACE, 'Name')

    @property
    def repeat(self):
        """Return the repeat value"""
        return self.player_props.Get(
            constants.MEDIA_PLAYER_IFACE, 'Repeat')

    @repeat.setter
    def repeat(self, value):
        """Possible values: "off", "singletrack", "alltracks" or "group"""
        self.player_props.Set(
            constants.MEDIA_PLAYER_IFACE, 'Repeat', value)

    @property
    def shuffle(self):
        """Return the shuffle value"""
        return self.player_props.Get(constants.MEDIA_PLAYER_IFACE, 'Shuffle')

    @shuffle.setter
    def shuffle(self, value):
        """"Possible values: "off", "alltracks" or "group" """
        self.player_props.Set(constants.MEDIA_PLAYER_IFACE, 'Shuffle', value)

    @property
    def status(self):
        """Return the status of the player
        Possible status: "playing", "stopped", "paused",
        "forward-seek", "reverse-seek" or "error" """
        return self.player_props.Get(constants.MEDIA_PLAYER_IFACE, 'Status')

    @property
    def subtype(self):
        """Return the player subtype"""
        return self.player_props.Get(constants.MEDIA_PLAYER_IFACE, 'Subtype')

    def type(self, player_type):
        """Player type. Possible values are:

                * "Audio"
                * "Video"
                * "Audio Broadcasting"
                * "Video Broadcasting"
        """
        self.player_props.Set(
            constants.MEDIA_PLAYER_IFACE, 'Type', player_type)

    @property
    def position(self):
        """Return the playback position in milliseconds."""
        return self.player_props.Get(constants.MEDIA_PLAYER_IFACE, 'Position')

    def next(self):
        """Goes the next track and play it."""
        self.player_methods.Next()

    def play(self):
        """Resume the playback."""
        self.player_methods.Play()

    def pause(self):
        """Pause the track."""
        self.player_methods.Pause()

    def stop(self):
        """Stops the playback."""
        self.player_methods.Stop()

    def previous(self):
        """Goes the previous track and play it"""
        self.player_methods.Previous()

    def fast_forward(self):
        """Fast forward playback, this action is only stopped
        when another method in this interface is called.
        """
        self.player_methods.FastForward()

    def rewind(self):
        """Rewind playback, this action is only stopped
        when another method in this interface is called.
        """
        self.player_methods.Rewind()
