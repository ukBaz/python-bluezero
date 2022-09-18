"""Example of how to create a Peripheral device/GATT Server"""
# Standard modules
import logging

# Bluezero modules
from bluezero import adapter
from bluezero import async_tools
from bluezero import observer
from bluezero import peripheral

TEST_SRV_UUID = '00000001-F00D-C0DE-C0C0-DEADBEEFCAFE'
WRT_RSP_UUID = '00000002-F00D-C0DE-C0C0-DEADBEEFCAFE'


def write_cb(value, options):
    print(f"{value:} - {options:}")


def main(adapter_address):
    logger = logging.getLogger('localGATT')
    logger.setLevel(logging.DEBUG)

    # Create peripheral
    test_srv = peripheral.Peripheral(adapter_address)
    # Add service
    test_srv.add_service(srv_id=1, uuid=TEST_SRV_UUID, primary=True)

    # Add characteristics
    test_srv.add_characteristic(srv_id=1, chr_id=1, uuid=WRT_RSP_UUID,
                                value=[], notifying=False,
                                flags=['write', 'write-without-response'],
                                read_callback=None,
                                write_callback=write_cb,
                                notify_callback=None
                                )

    # Publish peripheral and start event loop
    test_srv.publish()
    observer.Scanner.start_beacon_scan(on_eddystone_uid=print)
    mainloop = async_tools.EventLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        mainloop.quit()


if __name__ == '__main__':
    # Get the default adapter address and pass it to main
    main(list(adapter.Adapter.available())[0].address)
