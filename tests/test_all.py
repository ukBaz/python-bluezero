__author__ = 'barry'
import unittest
from bluezero.url_to_advert import url_to_advert


class NoSuffix(unittest.TestCase):
    def test(self):
        self.assertEqual(url_to_advert('http://camjam.me/', 0x10, 0x00),
                         [0x10, 0x00, 0x02, 0x63, 0x61, 0x6D, 0x6A, 0x61, 0x6D, 0x2E, 0x6D, 0x65, 0x2F])


class WithSuffix(unittest.TestCase):
    def test(self):
        self.assertEqual(url_to_advert('https://www.google.com', 0x10, 0x00),
                         [0x10, 0x00, 0x01, 0x67, 0x6f, 0x6f, 0x67, 0x6c, 0x65, 0x07])


class PostSuffix(unittest.TestCase):
    def test(self):
        self.assertEqual(url_to_advert('http://www.csr.com/about', 0x10, 0x00),
                         [0x10, 0x00, 0x00, 0x63, 0x73, 0x72, 0x00, 0x61, 0x62, 0x6f, 0x75, 0x74])


if __name__ == '__main__':
    unittest.main()
