"""
Code for create a Bluetooth Low Energy Observer (beacon scanner) application
"""
from collections import namedtuple
import uuid
import dbus
from bluezero import adapter
from bluezero import async_tools
from bluezero import tools

logger = tools.create_module_logger(__name__)
packet_callback = None

DEVICE_INTERFACE = 'org.bluez.Device1'
EDDYSTONE_SRV_UUID = '0000feaa-0000-1000-8000-00805f9b34fb'

EddyURL = namedtuple('EddyURL', ['url', 'tx_pwr', 'rssi'])
EddyUID = namedtuple('EddyUID', ['namespace', 'instance', 'tx_pwr', 'rssi'])
EddyTLM = namedtuple('EddyTLM',
                     ['version', 'battery', 'temperature', 'count', 'uptime',
                      'tx_pwr', 'rssi'])
iBeacon = namedtuple('iBeacon',  # pylint: disable=invalid-name
                     ['UUID', 'major', 'minor', 'tx_pwr', 'rssi'])
AltBeacon = namedtuple('AltBeacon',
                       ['UUID', 'major', 'minor', 'tx_pwr', 'rssi'])


def clean_beacon(dongle, device_path):
    """
    Remove beacon from BlueZ's `devices` list so every advert from a
    beacon is reported
    """
    logger.debug("Removing device %s", device_path)
    try:
        dongle.remove_device(device_path)
    except dbus.exceptions.DBusException as dbus_err:
        if dbus_err.get_dbus_name() == 'org.bluez.Error.DoesNotExist':
            logger.error("Device %s not available to remove", device_path)


def ble_16bit_match(uuid_16, srv_data):
    """
    Utility method to test 16 bit UUID against Bluetooth SIG 128 bit UUID
    used in service data

    :param uuid_16: 16 Bit UUID value
    :param srv_data:
    :return:
    """
    uuid_128 = f'0000{uuid_16}-0000-1000-8000-00805f9b34fb'
    return uuid_128 == list(srv_data.keys())[0]


class Scanner:
    """
    For scanning of Bluetooth Low Energy (BLE) beacons
    """
    mainloop = async_tools.EventLoop()
    on_eddystone_url = None
    on_eddystone_uid = None
    on_eddystone_tlm = None
    on_ibeacon = None
    on_altbeacon = None

    @classmethod
    def start_event_loop(cls):
        """
        Start the event loop
        """
        cls.mainloop.run()

    @classmethod
    def stop_scan(cls):
        """
        Stop scanning for beacons
        """
        cls.mainloop.quit()
        cls.dongle.stop_discovery()

    @classmethod
    def process_eddystone(cls, data, rssi):
        """
        Extract Eddystone data from advertisement service data

        :param data: Bytes from Service Data in advertisement
        :param rssi: Received Signal Strength value
        """
        _url_prefix_scheme = ['http://www.', 'https://www.',
                              'http://', 'https://', ]
        _url_encoding = ['.com/', '.org/', '.edu/', '.net/', '.info/',
                         '.biz/', '.gov/', '.com', '.org', '.edu',
                         '.net', '.info', '.biz', '.gov']
        tx_pwr = int.from_bytes([data[1]], 'big', signed=True)
        if data[0] == 0x00:
            namespace_id = int.from_bytes(data[2:12], 'big')
            instance_id = int.from_bytes(data[12:18], 'big')
            logger.info('\t\tEddystone UID: %s - %s \u2197 %s', namespace_id,
                        instance_id, tx_pwr)
            data = EddyUID(namespace_id, instance_id, tx_pwr, rssi)
            if cls.on_eddystone_uid:
                cls.on_eddystone_uid(data)
        elif data[0] == 0x10:
            prefix = data[2]
            encoded_url = data[3:]
            full_url = _url_prefix_scheme[prefix]
            for letter in encoded_url:
                if letter < len(_url_encoding):
                    full_url += _url_encoding[letter]
                else:
                    full_url += chr(letter)
            logger.info('\t\tEddystone URL: %s  \u2197 %s  \u2198 %s',
                        full_url, tx_pwr, rssi)
            data = EddyURL(url=full_url, tx_pwr=tx_pwr, rssi=int(rssi))
            if cls.on_eddystone_url:
                cls.on_eddystone_url(data)
        elif data[0] == 0x20:
            version = int(data[1])
            # Only support plain beacons ATM
            if version == 0:
                voltage = int.from_bytes(
                    data[2:4], byteorder='big', signed=False)
                temperature = int.from_bytes(
                    data[4:6], byteorder='big', signed=True)/256.0
                count = int.from_bytes(
                    data[6:10], byteorder='big', signed=False)
                time = int.from_bytes(
                    data[10:], byteorder='big', signed=False) / 10
                logger.info('\t\tEddystone TLM: %s, %s mV, %s C, %s, %s s '
                            '\u2197 %s  \u2198 %s',
                            version, voltage, temperature, count, time,
                            tx_pwr, rssi)
                data = EddyTLM(version, voltage, temperature, count, time,
                               tx_pwr, rssi)
                if cls.on_eddystone_tlm:
                    cls.on_eddystone_tlm(data)

    @classmethod
    def process_ibeacon(cls, data, rssi, beacon_type='iBeacon'):
        """
        Extract iBeacon or AltBeacon data from Manufacturer Data in an
        advertisement

        :param data: Bytes from manufacturer data
        :param rssi: Received Signal Strength value
        :param beacon_type: iBeacon or AltBeacon
        """
        beacon_uuid = uuid.UUID(bytes=bytes(data[2:18]))
        major = int.from_bytes(bytearray(data[18:20]), 'big', signed=False)
        minor = int.from_bytes(bytearray(data[20:22]), 'big', signed=False)
        tx_pwr = int.from_bytes([data[22]], 'big', signed=True)
        logger.info('%s: %s - %s - %s  \u2197 %s \u2198 %s', beacon_type,
                    beacon_uuid, major, minor, tx_pwr, rssi)
        if beacon_type == 'iBeacon' and cls.on_ibeacon:
            data = iBeacon(beacon_uuid, major, minor, tx_pwr, rssi)
            cls.on_ibeacon(data)
        elif beacon_type == 'AltBeacon' and cls.on_altbeacon:
            data = AltBeacon(beacon_uuid, major, minor, tx_pwr, rssi)
            cls.on_altbeacon(data)

    @classmethod
    def on_device_found(cls, bz_device_obj):
        """
        Callback to look at BLE advertisement to see if it is a recognised
        beacon and if it is, then call the relevant processing function

        :param bz_device_obj: Bluezero device object of discovered device
        """
        logger.debug("Found device: %s", bz_device_obj.remote_device_path)
        beacon_device = False
        rssi = bz_device_obj.RSSI
        service_data = bz_device_obj.service_data
        manufacturer_data = bz_device_obj.manufacturer_data
        if service_data and ble_16bit_match('feaa', service_data):
            beacon_device = True
            cls.process_eddystone(service_data[EDDYSTONE_SRV_UUID],
                                  rssi)
        elif manufacturer_data:
            for mfg_id in manufacturer_data:
                # iBeacon 0x004c
                if mfg_id == 0x004c and manufacturer_data[mfg_id][0] == 0x02:
                    beacon_device = True
                    cls.process_ibeacon(manufacturer_data[mfg_id], rssi)
                # AltBeacon 0xacbe
                elif all((mfg_id == 0xffff,
                          manufacturer_data[mfg_id][0:2] == [0xbe, 0xac])):
                    beacon_device = True
                    cls.process_ibeacon(manufacturer_data[mfg_id], rssi,
                                        beacon_type='AltBeacon')
                # elif mfg_id == 0x0310:
                #     print(f'\t\tBlue Maestro {manufacturer_data[mfg_id]}')
                #     remove_list.add(device_path)
        if beacon_device:
            clean_beacon(cls.dongle, bz_device_obj.remote_device_path)

    @classmethod
    def start_beacon_scan(cls,
                          on_eddystone_url=None,
                          on_eddystone_uid=None,
                          on_eddystone_tlm=None,
                          on_ibeacon=None,
                          on_altbeacon=None):
        """
        Start scan for beacons. Provided callback will be called if matching
        beacon type is found.
        All callbacks take one argument which is a named tuple with the fields
        relevant for that format.

        - Eddystone URL = ['url', 'tx_pwr', 'rssi']
        - Eddystone UID = ['namespace', 'instance', 'tx_pwr', 'rssi']
        - Eddystone TLM = ['version', 'voltage', 'temperature', 'count',
                           'time', 'tx_pwr', 'rssi']
        - iBeacon = ['UUID', 'major', 'minor', 'tx_pwr', 'rssi']
        - AltBeacon = ['UUID', 'major', 'minor', 'tx_pwr', 'rssi']

        :param on_eddystone_url: Callback for Eddystone URL format
        :param on_eddystone_uid: Callback for Eddystone UID format
        :param on_eddystone_tlm: Callback for Eddystone TLM format
        :param on_ibeacon: Callback for iBeacon format
        :param on_altbeacon: Callback for AltBeacon format
        """
        cls.dongle = adapter.Adapter()
        cls.on_eddystone_url = on_eddystone_url
        cls.on_eddystone_uid = on_eddystone_uid
        cls.on_eddystone_tlm = on_eddystone_tlm
        cls.on_ibeacon = on_ibeacon
        cls.on_altbeacon = on_altbeacon

        cls.dongle.on_device_found = cls.on_device_found

        cls.dongle.show_duplicates()
        cls.dongle.start_discovery()
        try:
            cls.start_event_loop()
        except KeyboardInterrupt:
            cls.stop_scan()


def scan_eddystone(on_data=None):
    """
    Provide a callback for 'on_data'. The callback will be run whenever
    an Eddystone URL packet is detected.

    :param on_data: A function to be called on Eddystone packet
    :return: None
    """
    try:
        Scanner.start_beacon_scan(on_eddystone_url=on_data)
    except KeyboardInterrupt:
        Scanner.stop_scan()
