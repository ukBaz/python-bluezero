"""Utility functions for python-bluezero."""


def int_to_uint16(value_in):
    bin_string = '{:016b}'.format(value_in)
    big_byte = int(bin_string[0:8], 2)
    little_byte = int(bin_string[8:16], 2)
    return [little_byte, big_byte]


def sint16_to_int(bytes):
    return int.from_bytes(bytes, byteorder='little', signed=True)


def bytes_to_xyz(bytes):
    x = sint16_to_int(bytes[0:2]) / 1000
    y = sint16_to_int(bytes[2:4]) / 1000
    z = sint16_to_int(bytes[4:6]) / 1000

    return [x, y, z]


def int_to_uint32(value_in):
    bin_string = '{0:032b}'.format(value_in)
    octet0 = int(bin_string[25:32], 2)
    octet1 = int(bin_string[17:24], 2)
    octet2 = int(bin_string[9:16], 2)
    octet3 = int(bin_string[0:8], 2)

    return [octet0, octet1, octet2,  octet3]


def url_to_advert(url, frame_type, tx_power):
    """
    Encode as specified
    https://github.com/google/eddystone/blob/master/eddystone-url/README.md
    :param url:
    :return:
    """
    prefix_sel = None
    prefix_start = None
    prefix_end = None
    suffix_sel = None
    suffix_start = None
    suffix_end = None

    prefix = ('http://www.', 'https://www.', 'http://', 'https://')

    suffix = ('.com/', '.org/', '.edu/', '.net/', '.info/', '.biz/', '.gov/',
              '.com', '.org', '.edu', '.net', '.info', '.biz', '.gov'
              )
    encode_search = True

    for x in prefix:
        if x in url and encode_search is True:
            # print('match prefix ' + url)
            prefix_sel = prefix.index(x)
            prefix_start = url.index(prefix[prefix_sel])
            prefix_end = len(prefix[prefix_sel]) + prefix_start
            encode_search = False

    encode_search = True
    for y in suffix:
        if y in url and encode_search is True:
            # print('match suffix ' + y)
            suffix_sel = suffix.index(y)
            suffix_start = url.index(suffix[suffix_sel])
            suffix_end = len(suffix[suffix_sel]) + suffix_start
            encode_search = False

    service_data = [frame_type]
    service_data.extend([tx_power])
    if suffix_start is None:
        suffix_start = len(url)
        service_data.extend([prefix_sel])
        for x in range(prefix_end, suffix_start):
            service_data.extend([ord(url[x])])
    elif suffix_end == len(url):
        service_data.extend([prefix_sel])
        for x in range(prefix_end, suffix_start):
            service_data.extend([ord(url[x])])
        service_data.extend([suffix_sel])
    else:
        service_data.extend([prefix_sel])
        for x in range(prefix_end, suffix_start):
            service_data.extend([ord(url[x])])
        service_data.extend([suffix_sel])
        for x in range(suffix_end, len(url)):
            service_data.extend([ord(url[x])])

    return service_data
