from bluezero import observer


def print_eddystone_values(data):
    """

    :param data:
    :return:
    """
    expected_keys = {'name space': 'hex_format',
                     'instance': 'hex_format',
                     'url': 'string_format',
                     'mac address': 'string_format',
                     'tx_power': 'int_format',
                     'rssi': 'int_format'}
    endian = 'big'

    print('New Eddystone data:')
    for prop in data:
        if prop in expected_keys:
            if expected_keys[prop] == 'string_format':
                print('\t{} = {}'.format(prop, data[prop]))
            if expected_keys[prop] == 'hex_format':
                print('\t{} = 0x{:X}'.format(prop,
                                             int.from_bytes(data[prop],
                                                            endian)))
            if expected_keys[prop] == 'int_format':
                print('\t{} = {}'.format(prop, int(data[prop])))


if __name__ == '__main__':
    observer.scan_eddystone(on_data=print_eddystone_values)
