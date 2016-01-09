
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

if __name__ == '__main__':
    url_to_advert('http://camjam.me/', 0x10, 0x00)
    url_to_advert('https://www.google.com', 0x10, 0x00)
    url_to_advert('http://www.csr.com/about', 0x10, 0x00)
