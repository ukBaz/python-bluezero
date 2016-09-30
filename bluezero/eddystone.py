"""
Level 1 file for creating Eddystone beacons
"""
from bluezero import tools
from bluezero import broadcaster


class EddystoneURL:
    """
    Eddystone is a Bluetooth Low Energy beacon profile released by
    Google in July 2015
    https://github.com/google/eddystone
    """
    def __init__(self, url, tx_power=0x08):
        """The Eddystone-URL frame broadcasts a URL using a compressed encoding
        format in order to fit more within the limited advertisement packet.
        :Example:

        >>> from bluezero import eddystone
        >>> eddystone.EddystoneURL('https://github.com/ukBaz')

        :param url: String containing URL e.g. ('http://camjam.me')
        :param tx_power:

        """
        service_data = tools.url_to_advert(url, 0x10, tx_power)
        if len(service_data) > 17:
            raise Exception('URL too long')
        url_beacon = broadcaster.Beacon()
        url_beacon.add_service_data('FEAA', service_data)
        url_beacon.start_beacon()
