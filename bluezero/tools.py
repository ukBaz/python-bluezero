"""Utility functions for python-bluezero."""
from enum import Enum
import logging
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


def sint16_to_int(byte_array):
    """
    Convert a signed 16-bit integer to integer

    :param byte_array:
    :return:
    """
    return int.from_bytes(byte_array, byteorder='little', signed=True)


def bytes_to_xyz(byte_array):
    """
    Split 6 byte long in integers representing x, y & z

    :param byte_array:
    :return:
    """
    x = sint16_to_int(byte_array[0:2]) / 1000  # pylint: disable=invalid-name
    y = sint16_to_int(byte_array[2:4]) / 1000  # pylint: disable=invalid-name
    z = sint16_to_int(byte_array[4:6]) / 1000  # pylint: disable=invalid-name

    return [x, y, z]


def int_to_uint32(value_in):
    """
    Convert integer to unsigned 32-bit (little endian)

    :param value_in:
    :return:
    """
    return list(value_in.to_bytes(4, byteorder='little', signed=False))


def bitwise_or_2lists(list1, list2):
    """
    Takes two bit patterns of equal length and performs the logical
    inclusive OR operation on each pair of corresponding bits
    """
    list_len = len(list2)
    return_list = [None] * list_len
    for i in range(list_len):
        return_list[i] = list1[i] | list2[i]
    return return_list


def bitwise_and_2lists(list1, list2):
    """
    Takes two bit patterns of equal length and performs the logical
    inclusive AND operation on each pair of corresponding bits
    """
    list_len = len(list2)
    return_list = [None] * list_len
    for i in range(list_len):
        return_list[i] = list1[i] & list2[i]
    return return_list


def bitwise_xor_2lists(list1, list2):
    """
    Takes two bit patterns of equal length and performs the logical
    inclusive XOR operation on each pair of corresponding bits
    """
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

    for domain in prefix:
        if domain in url and encode_search is True:
            # print('match prefix ' + url)
            prefix_sel = prefix.index(domain)
            prefix_start = url.index(prefix[prefix_sel])
            prefix_end = len(prefix[prefix_sel]) + prefix_start
            encode_search = False

    encode_search = True
    for tld in suffix:
        if tld in url and encode_search is True:
            # print('match suffix ' + y)
            suffix_sel = suffix.index(tld)
            suffix_start = url.index(suffix[suffix_sel])
            suffix_end = len(suffix[suffix_sel]) + suffix_start
            encode_search = False

    service_data = [frame_type]
    service_data.extend([tx_power])
    if suffix_start is None:
        suffix_start = len(url)
        service_data.extend([prefix_sel])
        for domain in range(prefix_end, suffix_start):
            service_data.extend([ord(url[domain])])
    elif suffix_end == len(url):
        service_data.extend([prefix_sel])
        for domain in range(prefix_end, suffix_start):
            service_data.extend([ord(url[domain])])
        service_data.extend([suffix_sel])
    else:
        service_data.extend([prefix_sel])
        for domain in range(prefix_end, suffix_start):
            service_data.extend([ord(url[domain])])
        service_data.extend([suffix_sel])
        for domain in range(suffix_end, len(url)):
            service_data.extend([ord(url[domain])])

    return service_data


def get_fn_parameters(fn):
    """ return the number of input parameters of the fn , None on error"""
    param_len = len(inspect.getfullargspec(fn).args)
    if inspect.ismethod(fn):
        param_len -= 1
    return param_len


def create_module_logger(module_name):
    """helper function to create logger in Bluezero modules"""
    logger = logging.getLogger(module_name)
    strm_hndlr = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    strm_hndlr.setFormatter(formatter)
    logger.addHandler(strm_hndlr)
    return logger

# Improve the above logger helper so that report level can be easily changed
# by users. This is not ready for inclusion but leaving it here in case anyone
# has some ideas
#
# class DebugLevels(Enum):
#     CRITICAL = 50
#     ERROR = 40
#     WARNING = 30
#     INFO = 20
#     DEBUG = 10
#     NOTSET = 0
#
#
# class BluezeroLogger:
#     def __init__(self, module_name):
#         self.logger = logging.getLogger(module_name)
#         ch = logging.StreamHandler()
#         formatter = logging.Formatter(
#             '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#         ch.setFormatter(formatter)
#         self.logger.addHandler(ch)
#         return self.logger
#
#     @property
#     def level(self):
#         return DebugLevels(self.logger.getEffectiveLevel()).name
#
#     @level.setter
#     def level(self, logger_level):
#         self.logger.setLevel()
