"""
Level 1 file for creating Eddystone beacons

Eddystone is a Bluetooth Low Energy beacon profile released by
Google in July 2015
https://github.com/google/eddystone

This is the broadcaster role which currently requires BlueZ to
have the experimental flag enabled
"""
from bluezero import tools
from bluezero import broadcaster


class EddystoneURL:
    """
    Create and start broadcasting a Eddystone URL beacon

    The Eddystone-URL frame broadcasts a URL using a compressed encoding
    format in order to fit more within the limited advertisement packet.
    :Example:

    >>> from bluezero import eddystone_beacon
    >>> eddystone_beacon.EddystoneURL('https://github.com/ukBaz')


    :param url: String containing URL e.g. ('http://camjam.me')
    :param tx_power: Value of Tx Power of advertisement (Not implemented)


    """
    def __init__(self, url, tx_power=0x08):
        """

        :param url: String containing URL e.g. ('http://camjam.me')
        :param tx_power: Value of Tx Power of advertisement (Not implemented)

        """
        service_data = tools.url_to_advert(url, 0x10, tx_power)
        if len(service_data) > 20:
            raise Exception('URL too long')
        url_beacon = broadcaster.Beacon()
        url_beacon.add_service_data('FEAA', service_data)
        url_beacon.start_beacon()
