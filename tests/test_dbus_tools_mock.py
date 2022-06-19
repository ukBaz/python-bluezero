import dbus
import dbusmock
import io
from pathlib import Path
import subprocess
from unittest import mock
from unittest.mock import patch
from tests.mock_eventloop import MockAsync

# Module under test
from bluezero import dbus_tools


class TestAdapterExample(dbusmock.DBusTestCase):
    """
    Test mocking bluetoothd
    """

    @classmethod
    def setUpClass(cls):
        here = Path(__file__).parent
        template = str(here.joinpath('dbusmock_templates', 'bluez_scan.py'))
        cls.start_system_bus()
        cls.dbus_con = cls.get_dbus(True)
        (cls.p_mock, cls.obj_bluez) = cls.spawn_server_template(
            template, {}, stdout=subprocess.PIPE)

    def setUp(self):
        self.obj_bluez.Reset()
        self.dbusmock = dbus.Interface(self.obj_bluez, dbusmock.MOCK_IFACE)
        self.dbusmock_bluez = dbus.Interface(self.obj_bluez, 'org.bluez.Mock')


    @classmethod
    def tearDownClass(cls):
        cls.stop_dbus(cls.system_bus_pid)
        cls.p_mock.terminate()
        cls.p_mock.wait()

    def test_dbus_string(self):
        result = dbus_tools.dbus_to_python(dbus.String("This is a test"))
        self.assertEqual(result, "This is a test")
        self.assertIsInstance(result, str)

    def test_dbus_int64(self):
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')

        result = dbus_tools.dbus_to_python(dbus.Int64(12))
        self.assertTrue(isinstance(result, int))

    def test_dbus_read_value(self):
        result = dbus_tools.dbus_to_python(dbus.Array([dbus.Byte(66),
                                                       dbus.Byte(97),
                                                       dbus.Byte(122)],
                                                      signature=dbus.Signature('y')))
        self.assertEqual(result, b"Baz")

    def test_dbus_dict(self):
        result = dbus_tools.dbus_to_python(dbus.Dictionary(
            {dbus.String('device'): dbus.ObjectPath('/org/bluez/hci0/dev_67_63_13_0D_37_01', variant_level=1),
             dbus.String('link'): dbus.String('LE', variant_level=1),
             dbus.String('mtu'): dbus.UInt16(512, variant_level=1)},
            signature=dbus.Signature('sv'))
        )
        self.assertDictEqual({'device': '/org/bluez/hci0/dev_67_63_13_0D_37_01',
                              'link': 'LE', 'mtu': 512},
                             result)

    def test_dbus_dict_adapter_props(self):
        dongle_props = dbus.Dictionary({
            dbus.String('Address'): dbus.String('11:22:33:44:55:66', variant_level=1),
            dbus.String('AddressType'): dbus.String('public', variant_level=1),
            dbus.String('Name'): dbus.String('test_machine', variant_level=1),
            dbus.String('Alias'): dbus.String('test_machine', variant_level=1),
            dbus.String('Class'): dbus.UInt32(786700, variant_level=1),
            dbus.String('Powered'): dbus.Boolean(True, variant_level=1),
            dbus.String('Discoverable'): dbus.Boolean(False, variant_level=1),
            dbus.String('DiscoverableTimeout'): dbus.UInt32(190, variant_level=1),
            dbus.String('Pairable'): dbus.Boolean(False, variant_level=1),
            dbus.String('PairableTimeout'): dbus.UInt32(120, variant_level=1),
            dbus.String('Discovering'): dbus.Boolean(False, variant_level=1),
            dbus.String('UUIDs'): dbus.Array(
                [dbus.String('0000110e-0000-1000-8000-00805f9b34fb'),
                 dbus.String('0000110a-0000-1000-8000-00805f9b34fb'),
                 dbus.String('00001200-0000-1000-8000-00805f9b34fb'),
                 dbus.String('00001112-0000-1000-8000-00805f9b34fb'),
                 dbus.String('0000110b-0000-1000-8000-00805f9b34fb'),
                 dbus.String('0000110c-0000-1000-8000-00805f9b34fb'),
                 dbus.String('00001800-0000-1000-8000-00805f9b34fb'),
                 dbus.String('00001108-0000-1000-8000-00805f9b34fb'),
                 dbus.String('00001801-0000-1000-8000-00805f9b34fb')],
                signature=dbus.Signature('s'), variant_level=1),
            dbus.String('Modalias'): dbus.String('usb:v1D6Bp0246d0535', variant_level=1)},
            signature=dbus.Signature('sv'))
        expected = {'Address': '11:22:33:44:55:66',
                    'AddressType': 'public',
                    'Alias': 'test_machine',
                    'Class': 786700,
                    'Discoverable': False,
                    'DiscoverableTimeout': 190,
                    'Discovering': False,
                    'Modalias': 'usb:v1D6Bp0246d0535',
                    'Name': 'test_machine',
                    'Pairable': False,
                    'PairableTimeout': 120,
                    'Powered': True,
                    'UUIDs': ['0000110e-0000-1000-8000-00805f9b34fb',
                              '0000110a-0000-1000-8000-00805f9b34fb',
                              '00001200-0000-1000-8000-00805f9b34fb',
                              '00001112-0000-1000-8000-00805f9b34fb',
                              '0000110b-0000-1000-8000-00805f9b34fb',
                              '0000110c-0000-1000-8000-00805f9b34fb',
                              '00001800-0000-1000-8000-00805f9b34fb',
                              '00001108-0000-1000-8000-00805f9b34fb',
                              '00001801-0000-1000-8000-00805f9b34fb']}
        result = dbus_tools.dbus_to_python(dongle_props)
        self.assertEqual(expected, result)

    def test_dbus_bool(self):
        result = dbus_tools.dbus_to_python(dbus.Boolean(True))
        self.assertTrue(isinstance(result, bool))

    def test_dbus_double(self):
        result = dbus_tools.dbus_to_python(dbus.Double(12.3))
        self.assertTrue(12.3, result)

    def test_dbus_byte(self):
        data = dbus.Byte(255)
        result = dbus_tools.dbus_to_python(data)
        self.assertEqual(0xFF, result)

    def test_dbus_byte_array1(self):
        data = dbus.Array([dbus.Byte(29)],
                          signature=dbus.Signature('y'))
        result = dbus_tools.dbus_to_python(data)
        self.assertEqual(b'\x1d', result)

    def test_str_to_dbusarray(self):
        expected = dbus.Array([dbus.Byte(70), dbus.Byte(111), dbus.Byte(120)],
                              signature=dbus.Signature('y'))
        result = dbus_tools.str_to_dbusarray('Fox')
        self.assertEqual(expected, result)

    def test_bytes_to_dbusarray(self):
        expected = dbus.Array([dbus.Byte(70), dbus.Byte(111), dbus.Byte(120)],
                              signature=dbus.Signature('y'))
        result = dbus_tools.bytes_to_dbusarray(b'Fox')
        self.assertEqual(expected, result)

    def test_bytes_to_dbusarray2(self):
        expected = dbus.Array([dbus.Byte(0), dbus.Byte(1), dbus.Byte(2)],
                              signature=dbus.Signature('y'))
        result = dbus_tools.bytes_to_dbusarray(b'\x00\x01\x02')
        self.assertEqual(expected, result)

    def test_get_service(self):
        result = dbus_tools.get_services('some/rubbish')
        self.assertListEqual([], result)

    def test_interfaces_added(self):
        with patch('logging.Logger.debug') as logger:
            result = dbus_tools.interfaces_added('/org/bluez/hci1/dev_00_11_22_33_44_55',
                                                 'org.bluez.Device1')
            logger.assert_called_once()

    def test_properties_changed(self):
        with patch('logging.Logger.debug') as logger:
            result = dbus_tools.properties_changed('org.bluez.Device1',
                                                   {'Connected': True},
                                                   {}, '/org/bluez/hci0')
            print(result)
            logger.assert_called_once()

    def test_get_property(self):
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')

        path_obj = dbus_tools.get_dbus_obj('/org/bluez/hci0')
        result = dbus_tools.get(path_obj, 'org.bluez.Adapter1', 'Address')
        self.assertEqual('00:01:02:03:04:05', result)

    def test_get_property_exception(self):
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')

        path_obj = dbus_tools.get_dbus_obj('/org/bluez/hci0')
        with self.assertRaises(dbus.exceptions.DBusException):
            result = dbus_tools.get(path_obj, 'org.bluez.AdapterXX', 'Address')

    def test_get_property_default(self):
        self.dbusmock_bluez.AddAdapter('hci0', 'My-Test-Device')

        path_obj = dbus_tools.get_dbus_obj('/org/bluez/hci0')
        result = dbus_tools.get(path_obj, 'org.bluez.Adapter1', 'address', 'xx')
        self.assertEqual('xx', result)
