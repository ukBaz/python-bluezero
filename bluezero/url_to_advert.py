
def url_to_advert(url):
    """
    Encode as specified https://github.com/google/eddystone/blob/master/eddystone-url/README.md
    :param url:
    :return:
    """
    # in = 'http://camjam.me/'
    out = 0x10, 0x00, 0x02, 0x63, 0x61, 0x6D, 0x6A, 0x61, 0x6D, 0x2E, 0x6D, 0x65, 0x2F
    # out = 4
    prefix = ['http://www.', 'https://www.', 'http://', 'https://']

    suffix = ['.com/', '.org/', '.edu/', '.net/', '.info/', '.biz/', '.gov/',
              '.com', '.org', '.edu', '.net', '.info', '.biz', '.gov',
              ]
    for x in prefix:
        print x
        if x in url:
            print 'match'
    for y in suffix:
        print y
    return out
