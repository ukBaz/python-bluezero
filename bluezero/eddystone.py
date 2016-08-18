"""
Level 1 file for creating Eddystone beacons
"""
from bluezero import tools
from bluezero import broadcaster

class EddystoneURL:
    def __init__(self, url):
        service_data = tools.url_to_advert(url, 0x10, 0x00)
        url_beacon = broadcaster.Beacon()
        url_beacon.add_service_data('FEAA', service_data)
        url_beacon.start_beacon()
