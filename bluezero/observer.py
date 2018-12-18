import aioblescan
from aioblescan.plugins import EddyStone

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
packet_callback = None


def _process_packet(data):
    """
    Filter BLE packets to only show Eddystone data
    before calling packet_callback
    :param data: BLE Packet data
    :return: None
    """
    logging.debug('Packet found')
    ev = aioblescan.HCI_Event()
    ev.decode(data)
    logging.debug('Using the following callback %s', packet_callback)
    if packet_callback is not None:
        eddystone_data = EddyStone().decode(ev)
        if eddystone_data:
            packet_callback(eddystone_data)


def scan_eddystone(on_data=None):
    """
    Provide a callback for 'on_data'. The callback will be run whenever
    an Eddystone packet is detected.

    :param on_data: A function to be called on Eddystone packet
    :return: None
    """
    global packet_callback
    mydev = 0
    event_loop = asyncio.get_event_loop()

    # First create and configure a raw socket
    mysocket = aioblescan.create_bt_socket(mydev)

    # create a connection with the raw socket
    fac = event_loop.create_connection(aioblescan.BLEScanRequester,
                                       sock=mysocket)
    # Start it
    conn, btctrl = event_loop.run_until_complete(fac)
    # Attach your processing
    btctrl.process = _process_packet
    packet_callback = on_data

    # Probe
    btctrl.send_scan_request()
    try:
        # event_loop.run_until_complete(coro)
        event_loop.run_forever()
    except KeyboardInterrupt:
        print('keyboard interrupt')
    finally:
        print('closing event loop')
        btctrl.stop_scan_request()
        conn.close()
        event_loop.close()
