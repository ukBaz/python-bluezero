import unittest
from bluezero import tools


class NoSuffix(unittest.TestCase):
    def test(self):
        self.assertEqual(
            tools.url_to_advert(
                'http://camjam.me/', 0x10, 0x00),
            [0x10, 0x00, 0x02, 0x63, 0x61, 0x6D, 0x6A,
             0x61, 0x6D, 0x2E, 0x6D, 0x65, 0x2F])


class WithSuffix(unittest.TestCase):
    def test(self):
        self.assertEqual(
            tools.url_to_advert(
                'https://www.google.com', 0x10, 0x00),
            [0x10, 0x00, 0x01, 0x67, 0x6f,
             0x6f, 0x67, 0x6c, 0x65, 0x07])


class PostSuffix(unittest.TestCase):
    def test(self):
        self.assertEqual(
            tools.url_to_advert(
                'http://www.csr.com/about', 0x10, 0x00),
            [0x10, 0x00, 0x00, 0x63, 0x73, 0x72,
             0x00, 0x61, 0x62, 0x6f, 0x75, 0x74])


class IntToUint32(unittest.TestCase):
    def test_with_zeros(self):
        little_endian = tools.int_to_uint32(2094)
        self.assertListEqual(little_endian, [0x2E, 0x08, 0x00, 0x00])

    def test_all_full(self):
        little_endian = tools.int_to_uint32(305419896)
        self.assertListEqual(little_endian, [0x78, 0x56, 0x34, 0x12])


if __name__ == '__main__':
    unittest.main()
