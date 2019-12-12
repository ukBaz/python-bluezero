"""Utility functions for python-bluezero."""
from sys import version_info
import inspect


def int_to_uint16(value_in):
    """
    Convert integer to Unsigned 16 bit little endian integer
    :param value_in: Integer < 65535 (0xFFFF)
    :return:
    """
    bin_string = '{:016b}'.format(value_in)
    big_byte = int(bin_string[0:8], 2)
    little_byte = int(bin_string[8:16], 2)
    return [little_byte, big_byte]


def sint16_to_int(bytes):
    """
    Convert a signed 16-bit integer to integer
    :param bytes:
    :return:
    """
    return int.from_bytes(bytes, byteorder='little', signed=True)


def bytes_to_xyz(bytes):
    """
    Split 6 byte long in integers representing x, y & z
    :param bytes:
    :return:
    """
    x = sint16_to_int(bytes[0:2]) / 1000
    y = sint16_to_int(bytes[2:4]) / 1000
    z = sint16_to_int(bytes[4:6]) / 1000

    return [x, y, z]


def int_to_uint32(value_in):
    """
    Convert integer to unsigned 32-bit (little endian)
    :param value_in:
    :return:
    """
    return [octet for octet in value_in.to_bytes(4,
                                                 byteorder='little',
                                                 signed=False)]


def bitwise_or_2lists(list1, list2):
    list_len = len(list1)
    return_list = [None] * list_len
    for i in range(list_len):
        return_list[i] = list1[i] | list2[i]
    return return_list


def bitwise_and_2lists(list1, list2):
    list_len = len(list1)
    return_list = [None] * list_len
    for i in range(list_len):
        return_list[i] = list1[i] & list2[i]
    return return_list


def bitwise_xor_2lists(list1, list2):
    list_len = len(list1)
    return_list = [None] * list_len
    for i in range(list_len):
        return_list[i] = list1[i] ^ list2[i]
    return return_list


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


def get_fn_parameters(fn):
    """ return the number of input parameters of the fn , None on error"""
    if version_info[0] < 3:
        try:
            # legacy python 2.x
            return len(inspect.getargspec(fn).args)
        except Exception as e:
            return None
    else:
        try:
            # python 3.x
            return len(inspect.getfullargspec(fn).args)
        except Exception as e:
            return None
