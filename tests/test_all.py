__author__ = 'barry'
import unittest
from bluezero.url_to_advert import url_to_advert


class simple_test(unittest.TestCase):


    def test(self):
        self.assertEqual(url_to_advert('http://camjam.me/'),
                         (0x10, 0x00, 0x02, 0x63, 0x61, 0x6D, 0x6A, 0x61, 0x6D, 0x2E, 0x6D, 0x65, 0x2F))

if __name__ == '__main__':
    unittest.main()