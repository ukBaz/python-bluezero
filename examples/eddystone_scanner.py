import logging
from bluezero import observer


def print_eddystone_url_values(data):
    """
    Callback to print data found with scan_eddystone
    :param data:
    :return:
    """
    print(f'Eddystone URL: {data.url} \u2197 {data.tx_pwr} \u2198 {data.rssi}')


def main():
    observer.scan_eddystone(on_data=print_eddystone_url_values)


if __name__ == '__main__':
    observer.logger.setLevel(logging.INFO)
    main()
