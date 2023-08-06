# -*- coding: utf-8 -*-

'''bluetoothd mock template

This creates the expected methods and properties of the object manager
org.bluez object (/), the manager object (/org/bluez), but no adapters or
devices.

This supports BlueZ 5 only.
'''

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.  See http://www.gnu.org/copyleft/lgpl.html for the full text
# of the license.

__author__ = 'Philip Withnall'
__email__ = 'philip.withnall@collabora.co.uk'
__copyright__ = '(c) 2013 Collabora Ltd.'
__license__ = 'LGPL 3+'

import time

import dbus

from dbusmock import OBJECT_MANAGER_IFACE, mockobject

BUS_NAME = 'org.bluez'
MAIN_OBJ = '/'
SYSTEM_BUS = True
IS_OBJECT_MANAGER = True

BLUEZ_MOCK_IFACE = 'org.bluez.Mock'
AGENT_MANAGER_IFACE = 'org.bluez.AgentManager1'
PROFILE_MANAGER_IFACE = 'org.bluez.ProfileManager1'
ADAPTER_IFACE = 'org.bluez.Adapter1'
MEDIA_IFACE = 'org.bluez.Media1'
NETWORK_SERVER_IFACE = 'org.bluez.Network1'
LEDADVERTISING_MNGR_IFACE = 'org.bluez.GattManager1'
DEVICE_IFACE = 'org.bluez.Device1'
GATT_MNGR_IFACE = 'org.bluez.GattManager1'
GATT_SRVC_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
GATT_DSCR_IFACE = 'org.bluez.GattDescriptor1'

# here = Path(__file__).parent
# device_json = Path.joinpath('device_db.json')
# with device_json.open() as input_db:
#     microbit_data = json.load(input_db)


def load(mock, parameters):
    mock.AddObject('/org/bluez', AGENT_MANAGER_IFACE, {}, [
        ('RegisterAgent', 'os', '', ''),
        ('RequestDefaultAgent', 'o', '', ''),
        ('UnregisterAgent', 'o', '', ''),
    ])

    bluez = mockobject.objects['/org/bluez']
    bluez.AddMethods(PROFILE_MANAGER_IFACE, [
        ('RegisterProfile', 'osa{sv}', '', ''),
        ('UnregisterProfile', 'o', '', ''),
    ])


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='ss', out_signature='s')
def AddAdapter(self, device_name, system_name):
    '''Convenience method to add a Bluetooth adapter

    You have to specify a device name which must be a valid part of an object
    path, e. g. "hci0", and an arbitrary system name (pretty hostname).

    Returns the new object path.
    '''
    path = '/org/bluez/' + device_name
    adapter_properties = {
        'UUIDs': dbus.Array([
            # Reference:
            # http://git.kernel.org/cgit/bluetooth/bluez.git/tree/lib/uuid.h
            # PNP
            '00001200-0000-1000-8000-00805f9b34fb',
            # Generic Access Profile
            '00001800-0000-1000-8000-00805f9b34fb',
            # Generic Attribute Profile
            '00001801-0000-1000-8000-00805f9b34fb',
            # Audio/Video Remote Control Profile (remote)
            '0000110e-0000-1000-8000-00805f9b34fb',
            # Audio/Video Remote Control Profile (target)
            '0000110c-0000-1000-8000-00805f9b34fb',
        ], variant_level=1),
        'Discoverable': dbus.Boolean(False, variant_level=1),
        'Discovering': dbus.Boolean(True, variant_level=1),
        'Pairable': dbus.Boolean(True, variant_level=1),
        'Powered': dbus.Boolean(True, variant_level=1),
        'Address': dbus.String('00:01:02:03:04:05', variant_level=1),
        'Alias': dbus.String(system_name, variant_level=1),
        'Modalias': dbus.String('usb:v1D6Bp0245d050A', variant_level=1),
        'Name': dbus.String(system_name, variant_level=1),
        # Reference:
        # http://bluetooth-pentest.narod.ru/software/
        # bluetooth_class_of_device-service_generator.html
        'Class': dbus.UInt32(268, variant_level=1),  # Computer, Laptop
        'DiscoverableTimeout': dbus.UInt32(180, variant_level=1),
        'PairableTimeout': dbus.UInt32(180, variant_level=1),
    }

    if device_name == 'hci1':
        adapter_properties['Address'] = 'AA:01:02:03:04:05'

    self.AddObject(path,
                   ADAPTER_IFACE,
                   # Properties
                   adapter_properties,
                   # Methods
                   [
                       ('RemoveDevice', 'o', '', ''),
                       ('StartDiscovery', '', '', DeviceDiscovery),
                       ('StopDiscovery', '', '', ''),
                       ('SetDiscoveryFilter', 'a{sv}', '', '')
                   ])
    adapter = mockobject.objects[path]

    adapter.AddMethods(MEDIA_IFACE, [
        ('RegisterEndpoint', 'oa{sv}', '', ''),
        ('UnregisterEndpoint', 'o', '', ''),
    ])
    adapter.AddMethods(NETWORK_SERVER_IFACE, [
        ('Register', 'ss', '', ''),
        ('Unregister', 's', '', ''),
    ])
    adapter.AddMethods(LEDADVERTISING_MNGR_IFACE, [
        ('RegisterAdvertisement', 'oa{sv}', '', ''),
        ('UnregisterAdvertisement', 'o', '', '')
    ])
    adapter.AddMethods(GATT_MNGR_IFACE, [
        ('RegisterApplication', 'oa{sv}', '', ''),
        ('UnregisterApplication', 'o', '', '')
    ])
    lea_mngr_properties = {
        'ActiveInstances': dbus.Byte(0),
        'SupportedIncludes': dbus.Array(["appearance", "local-name"],
                                        signature='s'),
        'SupportedInstances': dbus.Byte(5),
    }
    adapter.AddProperties(LEDADVERTISING_MNGR_IFACE,
                       dbus.Dictionary(
                           lea_mngr_properties
                       )
                       )
    """
    org.bluez.LEAdvertisingManager1     interface -         -                                        -
    .RegisterAdvertisement              method    oa{sv}    -                                        -
    .UnregisterAdvertisement            method    o         -                                        -
    .ActiveInstances                    property  y         1                                        emits-change
    .SupportedIncludes                  property  as        2 "appearance" "local-name"              emits-change
    .SupportedInstances                 property  y         4                                        emits-change
    .SupportedSecondaryChannels         property  as        -                                        emits-change
    """

    manager = mockobject.objects['/']
    manager.EmitSignal(OBJECT_MANAGER_IFACE, 'InterfacesAdded',
                       'oa{sa{sv}}', (
                           dbus.ObjectPath(path),
                           {
                               ADAPTER_IFACE: adapter_properties,
                               LEDADVERTISING_MNGR_IFACE: lea_mngr_properties
                            }
                       ))

    return path


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='sss', out_signature='s')
def AddDevice(self, adapter_device_name, device_address, alias):
    '''Convenience method to add a Bluetooth device

    You have to specify a device address which must be a valid Bluetooth
    address (e.g. 'AA:BB:CC:DD:EE:FF'). The alias is the human-readable name
    for the device (e.g. as set on the device itself), and the adapter device
    name is the device_name passed to AddAdapter.

    This will create a new, unpaired and unconnected device.

    Returns the new object path.
    '''
    device_name = 'dev_' + device_address.replace(':', '_').upper()
    adapter_path = '/org/bluez/' + adapter_device_name
    path = adapter_path + '/' + device_name

    if adapter_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Adapter %s does not exist.' % adapter_device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchAdapter')

    if path in microbit_data.keys():
        properties = microbit_data.get(path, {}).get(DEVICE_IFACE, {})
    else:
        properties = {
            'UUIDs': dbus.Array([], signature='s', variant_level=1),
            'Blocked': dbus.Boolean(False, variant_level=1),
            'Connected': dbus.Boolean(False, variant_level=1),
            'LegacyPairing': dbus.Boolean(False, variant_level=1),
            'Paired': dbus.Boolean(False, variant_level=1),
            'Trusted': dbus.Boolean(False, variant_level=1),
            'RSSI': dbus.Int16(-79, variant_level=1),  # arbitrary
            'Adapter': dbus.ObjectPath(adapter_path, variant_level=1),
            'Address': dbus.String(device_address, variant_level=1),
            'Alias': dbus.String(alias, variant_level=1),
            'Name': dbus.String(alias, variant_level=1),
        }

    self.AddObject(path,
                   DEVICE_IFACE,
                   # Properties
                   properties,
                   # Methods
                   [
                       ('CancelPairing', '', '', ''),
                       ('Connect', '', '',
                        'ret = self.ConnectMicroBit("%s", "%s")' % (adapter_device_name, device_address)),
                       ('ConnectProfile', 's', '', ''),
                       ('Disconnect', '', '', ''),
                       ('DisconnectProfile', 's', '', ''),
                       ('Pair', '', '', ''),
                   ])

    manager = mockobject.objects['/']
    manager.EmitSignal(OBJECT_MANAGER_IFACE, 'InterfacesAdded',
                       'oa{sa{sv}}', (
                           dbus.ObjectPath(path),
                           {DEVICE_IFACE: properties},
                       ))

    return path


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='ssi', out_signature='')
def PairDevice(self, adapter_device_name, device_address, class_=5898764):
    '''Convenience method to mark an existing device as paired.

    You have to specify a device address which must be a valid Bluetooth
    address (e.g. 'AA:BB:CC:DD:EE:FF'). The adapter device name is the
    device_name passed to AddAdapter.

    This unblocks the device if it was blocked.

    If the specified adapter or device don’t exist, a NoSuchAdapter or
    NoSuchDevice error will be returned on the bus.

    Returns nothing.
    '''
    device_name = 'dev_' + device_address.replace(':', '_').upper()
    adapter_path = '/org/bluez/' + adapter_device_name
    device_path = adapter_path + '/' + device_name

    if adapter_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Adapter %s does not exist.' % adapter_device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchAdapter')
    if device_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Device %s does not exist.' % device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchDevice')

    device = mockobject.objects[device_path]

    # Based off pairing with an Android phone.
    uuids = [
        '00001105-0000-1000-8000-00805f9b34fb',
        '0000110a-0000-1000-8000-00805f9b34fb',
        '0000110c-0000-1000-8000-00805f9b34fb',
        '00001112-0000-1000-8000-00805f9b34fb',
        '00001115-0000-1000-8000-00805f9b34fb',
        '00001116-0000-1000-8000-00805f9b34fb',
        '0000111f-0000-1000-8000-00805f9b34fb',
        '0000112f-0000-1000-8000-00805f9b34fb',
        '00001200-0000-1000-8000-00805f9b34fb',
    ]

    device.props[DEVICE_IFACE]['UUIDs'] = dbus.Array(uuids, variant_level=1)
    device.props[DEVICE_IFACE]['Paired'] = dbus.Boolean(True, variant_level=1)
    device.props[DEVICE_IFACE]['LegacyPairing'] = dbus.Boolean(True,
                                                               variant_level=1)
    device.props[DEVICE_IFACE]['Blocked'] = dbus.Boolean(False,
                                                         variant_level=1)

    try:
        device.props[DEVICE_IFACE]['Modalias']
    except KeyError:
        device.AddProperties(DEVICE_IFACE, {
            'Modalias': dbus.String('bluetooth:v000Fp1200d1436',
                                    variant_level=1),
            'Class': dbus.UInt32(class_, variant_level=1),
            'Icon': dbus.String('phone', variant_level=1),
        })

    device.EmitSignal(dbus.PROPERTIES_IFACE, 'PropertiesChanged', 'sa{sv}as', (
        DEVICE_IFACE,
        {
            'UUIDs': dbus.Array(uuids, variant_level=1),
            'Paired': dbus.Boolean(True, variant_level=1),
            'LegacyPairing': dbus.Boolean(True, variant_level=1),
            'Blocked': dbus.Boolean(False, variant_level=1),
            'Modalias': dbus.String('bluetooth:v000Fp1200d1436',
                                    variant_level=1),
            'Class': dbus.UInt32(class_, variant_level=1),
            'Icon': dbus.String('phone', variant_level=1),
        },
        [],
    ))


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='ss', out_signature='')
def BlockDevice(self, adapter_device_name, device_address):
    '''Convenience method to mark an existing device as blocked.

    You have to specify a device address which must be a valid Bluetooth
    address (e.g. 'AA:BB:CC:DD:EE:FF'). The adapter device name is the
    device_name passed to AddAdapter.

    This disconnects the device if it was connected.

    If the specified adapter or device don’t exist, a NoSuchAdapter or
    NoSuchDevice error will be returned on the bus.

    Returns nothing.
    '''
    device_name = 'dev_' + device_address.replace(':', '_').upper()
    adapter_path = '/org/bluez/' + adapter_device_name
    device_path = adapter_path + '/' + device_name

    if adapter_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Adapter %s does not exist.' % adapter_device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchAdapter')
    if device_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Device %s does not exist.' % device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchDevice')

    device = mockobject.objects[device_path]

    device.props[DEVICE_IFACE]['Blocked'] = dbus.Boolean(True, variant_level=1)
    device.props[DEVICE_IFACE]['Connected'] = dbus.Boolean(False,
                                                           variant_level=1)

    device.EmitSignal(dbus.PROPERTIES_IFACE, 'PropertiesChanged', 'sa{sv}as', (
        DEVICE_IFACE,
        {
            'Blocked': dbus.Boolean(True, variant_level=1),
            'Connected': dbus.Boolean(False, variant_level=1),
        },
        [],
    ))


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='ss', out_signature='')
def ConnectDevice(self, adapter_device_name, device_address):
    '''Convenience method to mark an existing device as connected.

    You have to specify a device address which must be a valid Bluetooth
    address (e.g. 'AA:BB:CC:DD:EE:FF'). The adapter device name is the
    device_name passed to AddAdapter.

    This unblocks the device if it was blocked.

    If the specified adapter or device don’t exist, a NoSuchAdapter or
    NoSuchDevice error will be returned on the bus.

    Returns nothing.
    '''
    device_name = 'dev_' + device_address.replace(':', '_').upper()
    adapter_path = '/org/bluez/' + adapter_device_name
    device_path = adapter_path + '/' + device_name

    if adapter_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Adapter %s does not exist.' % adapter_device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchAdapter')
    if device_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Device %s does not exist.' % device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchDevice')

    device = mockobject.objects[device_path]

    device.props[DEVICE_IFACE]['Blocked'] = dbus.Boolean(False,
                                                         variant_level=1)
    device.props[DEVICE_IFACE]['Connected'] = dbus.Boolean(True,
                                                           variant_level=1)

    device.EmitSignal(dbus.PROPERTIES_IFACE, 'PropertiesChanged', 'sa{sv}as', (
        DEVICE_IFACE,
        {
            'Blocked': dbus.Boolean(False, variant_level=1),
            'Connected': dbus.Boolean(True, variant_level=1),
        },
        [],
    ))


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='oa{sv}', out_signature='s')
def AddGattService(self,
                   path,
                   service_props):
    self.AddObject(path,
                   GATT_SRVC_IFACE,
                   # Properties
                   service_props,
                   # Methods
                   [])

    print('Adding props', service_props)
    manager = mockobject.objects['/']
    manager.EmitSignal(OBJECT_MANAGER_IFACE, 'InterfacesAdded',
                       'oa{sa{sv}}', (
                           dbus.ObjectPath(path),
                           {GATT_SRVC_IFACE: service_props},
                       ))

    return path


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='sa{sv}', out_signature='s')
def AddGattCharacteristic(self, path, charc_props):
    self.AddObject(path,
                   GATT_CHRC_IFACE,
                   # Properties
                   charc_props,
                   # Methods
                   [
                       ('AcquireNotify', 'a{sv}', 'hq', ''),
                       ('AcquireWrite', 'a{sv}', 'hq', ''),
                       ('ReadValue', 'a{sv}', 'ay',
                        'ret = self.GattReadValue("%s", args[0])' % path),
                       ('StartNotify', '', '', ''),
                       ('StopNotify', '', '', ''),
                       ('WriteValue', 'aya{sv}',   '',
                        'ret = self.GattWriteValue("%s", args[0], args[1])' % path),
                   ])

    manager = mockobject.objects['/']
    manager.EmitSignal(OBJECT_MANAGER_IFACE, 'InterfacesAdded',
                       'oa{sa{sv}}', (
                           dbus.ObjectPath(path),
                           {GATT_CHRC_IFACE: charc_props},
                       ))

    return path


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='ss', out_signature='')
def DisconnectDevice(self, adapter_device_name, device_address):
    '''Convenience method to mark an existing device as disconnected.

    You have to specify a device address which must be a valid Bluetooth
    address (e.g. 'AA:BB:CC:DD:EE:FF'). The adapter device name is the
    device_name passed to AddAdapter.

    This does not change the device’s blocked status.

    If the specified adapter or device don’t exist, a NoSuchAdapter or
    NoSuchDevice error will be returned on the bus.

    Returns nothing.
    '''
    device_name = 'dev_' + device_address.replace(':', '_').upper()
    adapter_path = '/org/bluez/' + adapter_device_name
    device_path = adapter_path + '/' + device_name

    if adapter_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Adapter %s does not exist.' % adapter_device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchAdapter')
    if device_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Device %s does not exist.' % device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchDevice')

    device = mockobject.objects[device_path]

    device.props[DEVICE_IFACE]['Connected'] = dbus.Boolean(False,
                                                           variant_level=1)
    device.EmitSignal(dbus.PROPERTIES_IFACE, 'PropertiesChanged', 'sa{sv}as', (
        DEVICE_IFACE,
        {
            'Connected': dbus.Boolean(False, variant_level=1),
        },
        [],
    ))


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='ssqaysy', out_signature='s')
def AddBeacon(self,
              adapter_device_name='hci0',
              device_address='11:01:02:03:04:05',
              manf_id=None,
              manf_data=None,
              service_uuid=None,
              service_data=None,
              ):
    """Convenience method to add a Bluetooth device acting as AltBeacon

    You have to specify a device address which must be a valid Bluetooth
    address (e.g. 'AA:BB:CC:DD:EE:FF'). The alias is the human-readable name
    for the device (e.g. as set on the device itself), and the adapter device
    name is the device_name passed to AddAdapter.

    This will create a new, unpaired and unconnected device.

    Returns the new object path.
    """
    device_name = 'dev_' + device_address.replace(':', '_').upper()
    adapter_path = '/org/bluez/' + adapter_device_name
    path = adapter_path + '/' + device_name

    if adapter_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Adapter %s does not exist.' % adapter_device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchAdapter')

    properties = {
        'UUIDs': dbus.Array([], signature='s', variant_level=1),
        'Blocked': dbus.Boolean(False, variant_level=1),
        'Connected': dbus.Boolean(False, variant_level=1),
        'LegacyPairing': dbus.Boolean(False, variant_level=1),
        'Paired': dbus.Boolean(False, variant_level=1),
        'Trusted': dbus.Boolean(False, variant_level=1),
        'RSSI': dbus.Int16(-61, variant_level=1),  # arbitrary
        'Adapter': dbus.ObjectPath(adapter_path, variant_level=1),
        'Address': dbus.String(device_address, variant_level=1),
        'AddressType': dbus.String("random"),
        'Alias': dbus.String("40-A1-82-A6-BB-3D", variant_level=1),
    }
    if service_uuid:
        properties['UUIDs'].append(service_uuid)
        properties['ServiceData'] = dbus.Dictionary({service_uuid: service_data})
    if manf_id:
        properties['ManufacturerData'] = dbus.Dictionary({manf_id: manf_data})
    self.AddObject(path,
                   DEVICE_IFACE,
                   # Properties
                   properties,
                   # Methods
                   [
                       ('CancelPairing', '', '', ''),
                       ('Connect', '', '', ""),
                       ('ConnectProfile', 's', '', ''),
                       ('Disconnect', '', '', ''),
                       ('DisconnectProfile', 's', '', ''),
                       ('Pair', '', '', ''),
                   ])

    manager = mockobject.objects['/']
    manager.EmitSignal(OBJECT_MANAGER_IFACE, 'InterfacesAdded',
                       'oa{sa{sv}}', (
                           dbus.ObjectPath(path),
                           {DEVICE_IFACE: properties},
                       ))


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='', out_signature='')
def DeviceDiscovery(adapter):
    # Eddystone URL Beacon
    AddBeacon(adapter, 'hci0', '11:22:33:44:55:66',
              service_uuid='0000feaa-0000-1000-8000-00805f9b34fb',
              service_data=[16, 8, 1, 98, 108, 117, 101, 116, 111,
                            111, 116, 104, 7])
    # Eddystone UID Beacon
    AddBeacon(adapter, 'hci0', '11:22:33:44:55:99',
              service_uuid='0000feaa-0000-1000-8000-00805f9b34fb',
              service_data=[0, 191, 0, 0, 0, 0, 0, 69, 97, 114, 116, 104,
                            0, 0, 0, 0, 0, 11])
    # # AltBeacon
    AddBeacon(adapter, 'hci0', '11:22:33:44:55:77',
              manf_id=65535,
              manf_data=[190, 172, 72, 37, 62, 89, 114, 36, 68, 99,
                         185, 184, 3, 63, 250, 181, 202, 254, 97, 99,
                         101, 107, 188, 0])
    # # iBeacon
    AddBeacon(adapter, 'hci0', '11:22:33:44:55:88',
              manf_id=76,
              manf_data=[2, 21, 106, 177, 124, 23, 244, 123, 77, 65, 128,
                         54, 82, 106, 238, 210, 47, 115, 1, 22, 3, 104,
                         191])


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='ss', out_signature='')
def ConnectMicroBit(self, adapter_name, device_address):
    print('In connect microbit')
    upper_address = device_address.upper().replace(":", "_")
    dev_path = f'/org/bluez/{adapter_name}/dev_{upper_address}'
    device = mockobject.objects[dev_path]

    self.ConnectDevice(adapter_name, upper_address)

    for path in microbit_data:
        srvc_props = microbit_data[path].get(GATT_SRVC_IFACE)
        if srvc_props:
            del srvc_props['Includes']
            print('adding service', srvc_props)
            self.AddGattService(dbus.ObjectPath(path),
                                dbus.Dictionary(srvc_props,
                                                signature='sv'))
        chrc_props = microbit_data[path].get(GATT_CHRC_IFACE)
        if chrc_props:
            print('add characteristic')
            chrc_props = dbus.Dictionary(chrc_props, signature='sv')
            chrc_props['Value'] = dbus.Array(chrc_props['Value'], signature='y')
            self.AddGattCharacteristic(dbus.ObjectPath(path), chrc_props)

    device.props[DEVICE_IFACE]['ServicesResolved'] = dbus.Boolean(True, variant_level=1)

    device.EmitSignal(dbus.PROPERTIES_IFACE, 'PropertiesChanged', 'sa{sv}as', (
        DEVICE_IFACE,
        {
            'ServicesResolved': dbus.Boolean(True, variant_level=1),
        },
        [],
    ))


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='oa{sv}', out_signature='ay')
def GattReadValue(self, path, options):
    gatt_chrc = mockobject.objects[path]
    gatt_chrc.call_log.append((int(time.time()), 'ReadValue', [options]))
    # return microbit_data[path].get(GATT_CHRC_IFACE, {}).get('Value')
    return gatt_chrc.Get(GATT_CHRC_IFACE, 'Value')


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='oaya{sv}', out_signature='')
def GattWriteValue(self, path, value, options):
    # microbit_data[path][GATT_CHRC_IFACE]['Value'] = dbus.Array(value)
    gatt_chrc = mockobject.objects[path]
    gatt_chrc.Set(GATT_CHRC_IFACE, 'Value', value)
    gatt_chrc.call_log.append((int(time.time()), 'WriteValue', [value, options]))
    if path == '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028/char0029':
        tx_path = '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028/char002b'
        tx_obj = mockobject.objects[tx_path]
        tx_obj.EmitSignal(dbus.PROPERTIES_IFACE,
                          'PropertiesChanged',
                          'sa{sv}as', (
                              GATT_CHRC_IFACE,
                              {
                                  'Value': dbus.Array(value, variant_level=1),
                              },
                              [],
                          ))


microbit_data = {
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D": {'org.freedesktop.DBus.Introspectable': {},
                                              'org.bluez.Device1': {'Address': 'E9:06:4D:45:FC:8D',
                                                                    'AddressType': 'random',
                                                                    'Name': 'BBC micro:bit [tetog]',
                                                                    'Alias': 'BBC micro:bit [tetog]', 'Paired': False,
                                                                    'Trusted': False, 'Blocked': False,
                                                                    'LegacyPairing': False, 'Connected': False,
                                                                    'UUIDs': ['00001800-0000-1000-8000-00805f9b34fb',
                                                                              '00001801-0000-1000-8000-00805f9b34fb',
                                                                              '0000180a-0000-1000-8000-00805f9b34fb',
                                                                              '0000fe59-0000-1000-8000-00805f9b34fb',
                                                                              'e95d0753-251d-470a-a062-fa1922dfa9a8',
                                                                              'e95d6100-251d-470a-a062-fa1922dfa9a8',
                                                                              'e95d93af-251d-470a-a062-fa1922dfa9a8',
                                                                              'e95d9882-251d-470a-a062-fa1922dfa9a8',
                                                                              'e95dd91d-251d-470a-a062-fa1922dfa9a8',
                                                                              'e97dd91d-251d-470a-a062-fa1922dfa9a8'],
                                                                    'Adapter': '/org/bluez/hci0',
                                                                    'ServicesResolved': False},
                                              'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service003c": {'org.freedesktop.DBus.Introspectable': {},
                                                          'org.bluez.GattService1': {
                                                              'UUID': 'e95d6100-251d-470a-a062-fa1922dfa9a8',
                                                              'Device': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D',
                                                              'Primary': True, 'Includes': []},
                                                          'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service003c/char0040": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95d1b25-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service003c',
                                                                       'Value': [], 'Flags': ['read', 'write']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service003c/char003d": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95d9250-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service003c',
                                                                       'Value': [27], 'Notifying': False,
                                                                       'Flags': ['read', 'notify'],
                                                                       'NotifyAcquired': False},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service003c/char003d/desc003f": {'org.freedesktop.DBus.Introspectable': {},
                                                                            'org.bluez.GattDescriptor1': {
                                                                                'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                                                                'Characteristic': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service003c/char003d',
                                                                                'Value': []},
                                                                            'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0035": {'org.freedesktop.DBus.Introspectable': {},
                                                          'org.bluez.GattService1': {
                                                              'UUID': 'e95dd91d-251d-470a-a062-fa1922dfa9a8',
                                                              'Device': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D',
                                                              'Primary': True, 'Includes': []},
                                                          'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0035/char003a": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95d0d2d-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0035',
                                                                       'Value': [20, 0], 'Flags': ['read', 'write']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0035/char0038": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95d93ee-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0035',
                                                                       'Value': [], 'Flags': ['write']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0035/char0036": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95d7b77-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0035',
                                                                       'Value': [14, 16, 16, 16, 14],
                                                                       'Flags': ['read', 'write']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service002e": {'org.freedesktop.DBus.Introspectable': {},
                                                          'org.bluez.GattService1': {
                                                              'UUID': 'e95d9882-251d-470a-a062-fa1922dfa9a8',
                                                              'Device': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D',
                                                              'Primary': True, 'Includes': []},
                                                          'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service002e/char0032": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95dda91-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service002e',
                                                                       'Value': [1], 'Notifying': False,
                                                                       'Flags': ['read', 'notify'],
                                                                       'NotifyAcquired': False},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service002e/char0032/desc0034": {'org.freedesktop.DBus.Introspectable': {},
                                                                            'org.bluez.GattDescriptor1': {
                                                                                'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                                                                'Characteristic': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service002e/char0032',
                                                                                'Value': []},
                                                                            'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service002e/char002f": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95dda90-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service002e',
                                                                       'Value': [1], 'Notifying': False,
                                                                       'Flags': ['read', 'notify'],
                                                                       'NotifyAcquired': False},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service002e/char002f/desc0031": {'org.freedesktop.DBus.Introspectable': {},
                                                                            'org.bluez.GattDescriptor1': {
                                                                                'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                                                                'Characteristic': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service002e/char002f',
                                                                                'Value': []},
                                                                            'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0028": {'org.freedesktop.DBus.Introspectable': {},
                                                          'org.bluez.GattService1': {
                                                              'UUID': 'e95d0753-251d-470a-a062-fa1922dfa9a8',
                                                              'Device': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D',
                                                              'Primary': True, 'Includes': []},
                                                          'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0028/char002c": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95dfb24-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0028',
                                                                       'Value': [], 'Flags': ['read', 'write']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0028/char0029": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95dca4b-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0028',
                                                                       'Value': [140, 1, 140, 3, 144, 255],
                                                                       'Notifying': False, 'Flags': ['read', 'notify'],
                                                                       'NotifyAcquired': False},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0028/char0029/desc002b": {'org.freedesktop.DBus.Introspectable': {},
                                                                            'org.bluez.GattDescriptor1': {
                                                                                'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                                                                'Characteristic': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0028/char0029',
                                                                                'Value': []},
                                                                            'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d": {'org.freedesktop.DBus.Introspectable': {},
                                                          'org.bluez.GattService1': {
                                                              'UUID': 'e95d93af-251d-470a-a062-fa1922dfa9a8',
                                                              'Device': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D',
                                                              'Primary': True, 'Includes': []},
                                                          'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d/char0025": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95db84c-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d',
                                                                       'Value': [], 'Notifying': False,
                                                                       'Flags': ['read', 'notify'],
                                                                       'NotifyAcquired': False},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d/char0025/desc0027": {'org.freedesktop.DBus.Introspectable': {},
                                                                            'org.bluez.GattDescriptor1': {
                                                                                'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                                                                'Characteristic': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d/char0025',
                                                                                'Value': []},
                                                                            'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d/char0023": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95d23c4-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d',
                                                                       'Value': [], 'Flags': ['write']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d/char0021": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95d5404-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d',
                                                                       'Value': [],
                                                                       'Flags': ['write-without-response', 'write'],
                                                                       'WriteAcquired': False},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d/char001e": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e95d9775-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d',
                                                                       'Value': [], 'Notifying': False,
                                                                       'Flags': ['read', 'notify'],
                                                                       'NotifyAcquired': False},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d/char001e/desc0020": {'org.freedesktop.DBus.Introspectable': {},
                                                                            'org.bluez.GattDescriptor1': {
                                                                                'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                                                                'Characteristic': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service001d/char001e',
                                                                                'Value': []},
                                                                            'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0016": {'org.freedesktop.DBus.Introspectable': {},
                                                          'org.bluez.GattService1': {
                                                              'UUID': '0000180a-0000-1000-8000-00805f9b34fb',
                                                              'Device': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D',
                                                              'Primary': True, 'Includes': []},
                                                          'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0016/char001b": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': '00002a26-0000-1000-8000-00805f9b34fb',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0016',
                                                                       'Value': [], 'Flags': ['read']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0016/char0019": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': '00002a25-0000-1000-8000-00805f9b34fb',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0016',
                                                                       'Value': [], 'Flags': ['read']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0016/char0017": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': '00002a24-0000-1000-8000-00805f9b34fb',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0016',
                                                                       'Value': [], 'Flags': ['read']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0012": {'org.freedesktop.DBus.Introspectable': {},
                                                          'org.bluez.GattService1': {
                                                              'UUID': 'e97dd91d-251d-470a-a062-fa1922dfa9a8',
                                                              'Device': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D',
                                                              'Primary': True, 'Includes': []},
                                                          'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0012/char0013": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': 'e97d3b10-251d-470a-a062-fa1922dfa9a8',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0012',
                                                                       'Value': [], 'Notifying': False,
                                                                       'Flags': ['write-without-response', 'notify'],
                                                                       'WriteAcquired': False, 'NotifyAcquired': False},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0012/char0013/desc0015": {'org.freedesktop.DBus.Introspectable': {},
                                                                            'org.bluez.GattDescriptor1': {
                                                                                'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                                                                'Characteristic': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service0012/char0013',
                                                                                'Value': []},
                                                                            'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service000e": {'org.freedesktop.DBus.Introspectable': {},
                                                          'org.bluez.GattService1': {
                                                              'UUID': '0000fe59-0000-1000-8000-00805f9b34fb',
                                                              'Device': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D',
                                                              'Primary': True, 'Includes': []},
                                                          'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service000e/char000f": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': '8ec90004-f315-4f60-9fb8-838830daea50',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service000e',
                                                                       'Value': [], 'Notifying': False,
                                                                       'Flags': ['write', 'indicate']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service000e/char000f/desc0011": {'org.freedesktop.DBus.Introspectable': {},
                                                                            'org.bluez.GattDescriptor1': {
                                                                                'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                                                                'Characteristic': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service000e/char000f',
                                                                                'Value': []},
                                                                            'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service000a": {'org.freedesktop.DBus.Introspectable': {},
                                                          'org.bluez.GattService1': {
                                                              'UUID': '00001801-0000-1000-8000-00805f9b34fb',
                                                              'Device': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D',
                                                              'Primary': True, 'Includes': []},
                                                          'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service000a/char000b": {'org.freedesktop.DBus.Introspectable': {},
                                                                   'org.bluez.GattCharacteristic1': {
                                                                       'UUID': '00002a05-0000-1000-8000-00805f9b34fb',
                                                                       'Service': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service000a',
                                                                       'Value': [], 'Notifying': False,
                                                                       'Flags': ['indicate']},
                                                                   'org.freedesktop.DBus.Properties': {}},
    "/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service000a/char000b/desc000d": {'org.freedesktop.DBus.Introspectable': {},
                                                                            'org.bluez.GattDescriptor1': {
                                                                                'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                                                                'Characteristic': '/org/bluez/hci0/dev_E9_06_4D_45_FC_8D/service000a/char000b',
                                                                                'Value': []},
                                                                            'org.freedesktop.DBus.Properties': {}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02': {
        'org.bluez.Device1': {'Address': 'DD:02:02:02:02:02', 'AddressType': 'random',
                              'Name': 'BBC micro:bit',
                              'Alias': 'BBC micro:bit', 'Paired': True, 'Trusted': False, 'Blocked': False,
                              'LegacyPairing': False, 'Connected': False,
                              'UUIDs': ['00001800-0000-1000-8000-00805f9b34fb', '00001801-0000-1000-8000-00805f9b34fb',
                                        '0000180a-0000-1000-8000-00805f9b34fb', '0000fe59-0000-1000-8000-00805f9b34fb',
                                        '6e400001-b5a3-f393-e0a9-e50e24dcca9e', 'e95d0753-251d-470a-a062-fa1922dfa9a8',
                                        'e95d127b-251d-470a-a062-fa1922dfa9a8', 'e95d6100-251d-470a-a062-fa1922dfa9a8',
                                        'e95d93af-251d-470a-a062-fa1922dfa9a8', 'e95d9882-251d-470a-a062-fa1922dfa9a8',
                                        'e95dd91d-251d-470a-a062-fa1922dfa9a8', 'e97dd91d-251d-470a-a062-fa1922dfa9a8'],
                              'Adapter': '/org/bluez/hci0', 'ServicesResolved': False}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service004c': {
        'org.bluez.GattService1': {'UUID': 'e95d6100-251d-470a-a062-fa1922dfa9a8',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service004c/char0050': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95d1b25-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service004c',
                                          'Value': [0xe8, 0x03], 'Flags': ['read', 'write']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service004c/char004d': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95d9250-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service004c', 'Value': [],
                                          'Notifying': False, 'Flags': ['read', 'notify'], 'NotifyAcquired': False}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service004c/char004d/desc004f': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service004c/char004d',
                                      'Value': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0045': {
        'org.bluez.GattService1': {'UUID': 'e95dd91d-251d-470a-a062-fa1922dfa9a8',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0045/char004a': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95d0d2d-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0045', 'Value': [],
                                          'Flags': ['read', 'write']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0045/char0048': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95d93ee-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0045', 'Value': [],
                                          'Flags': ['write']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0045/char0046': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95d7b77-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0045', 'Value': [],
                                          'Flags': ['read', 'write']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b': {
        'org.bluez.GattService1': {'UUID': 'e95d127b-251d-470a-a062-fa1922dfa9a8',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b/char0042': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95d8d00-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b', 'Value': [],
                                          'Notifying': False, 'Flags': ['read', 'write', 'notify'],
                                          'NotifyAcquired': False}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b/char0042/desc0044': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b/char0042',
                                      'Value': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b/char0040': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95dd822-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b', 'Value': [],
                                          'Flags': ['write']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b/char003e': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95db9fe-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b', 'Value': [],
                                          'Flags': ['read', 'write']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b/char003c': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95d5899-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service003b', 'Value': [],
                                          'Flags': ['read', 'write']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0034': {
        'org.bluez.GattService1': {'UUID': 'e95d9882-251d-470a-a062-fa1922dfa9a8',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0034/char0038': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95dda91-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0034', 'Value': [],
                                          'Notifying': False, 'Flags': ['read', 'notify'], 'NotifyAcquired': False}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0034/char0038/desc003a': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0034/char0038',
                                      'Value': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0034/char0035': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95dda90-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0034', 'Value': [],
                                          'Notifying': False, 'Flags': ['read', 'notify'], 'NotifyAcquired': False}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0034/char0035/desc0037': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0034/char0035',
                                      'Value': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service002e': {
        'org.bluez.GattService1': {'UUID': 'e95d0753-251d-470a-a062-fa1922dfa9a8',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service002e/char0032': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95dfb24-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service002e', 'Value': [],
                                          'Flags': ['read', 'write']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service002e/char002f': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95dca4b-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service002e', 'Value': [],
                                          'Notifying': False, 'Flags': ['read', 'notify'], 'NotifyAcquired': False}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service002e/char002f/desc0031': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service002e/char002f',
                                      'Value': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028': {
        'org.bluez.GattService1': {'UUID': '6e400001-b5a3-f393-e0a9-e50e24dcca9e',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028/char002b': {
        'org.bluez.GattCharacteristic1': {'UUID': '6e400002-b5a3-f393-e0a9-e50e24dcca9e',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028', 'Value': [51],
                                          'Notifying': False, 'Flags': ['indicate']},
        'org.freedesktop.DBus.Properties': {}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028/char002b/desc002d': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028/char002b',
                                      'Value': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028/char0029': {
        'org.bluez.GattCharacteristic1': {'UUID': '6e400003-b5a3-f393-e0a9-e50e24dcca9e',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0028', 'Value': [],
                                          'Flags': ['write-without-response', 'write'], 'WriteAcquired': False},
        'org.freedesktop.DBus.Properties': {}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d': {
        'org.bluez.GattService1': {'UUID': 'e95d93af-251d-470a-a062-fa1922dfa9a8',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d/char0025': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95db84c-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d', 'Value': [],
                                          'Notifying': False, 'Flags': ['read', 'notify'], 'NotifyAcquired': False}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d/char0025/desc0027': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d/char0025',
                                      'Value': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d/char0023': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95d23c4-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d', 'Value': [],
                                          'Flags': ['write']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d/char0021': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95d5404-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d', 'Value': [],
                                          'Flags': ['write-without-response', 'write'], 'WriteAcquired': False}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d/char001e': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e95d9775-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d', 'Value': [],
                                          'Notifying': False, 'Flags': ['read', 'notify'], 'NotifyAcquired': False}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d/char001e/desc0020': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service001d/char001e',
                                      'Value': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0016': {
        'org.bluez.GattService1': {'UUID': '0000180a-0000-1000-8000-00805f9b34fb',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0016/char001b': {
        'org.bluez.GattCharacteristic1': {'UUID': '00002a26-0000-1000-8000-00805f9b34fb',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0016', 'Value': [],
                                          'Flags': ['read']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0016/char0019': {
        'org.bluez.GattCharacteristic1': {'UUID': '00002a25-0000-1000-8000-00805f9b34fb',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0016', 'Value': [],
                                          'Flags': ['read']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0016/char0017': {
        'org.bluez.GattCharacteristic1': {'UUID': '00002a24-0000-1000-8000-00805f9b34fb',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0016', 'Value': [],
                                          'Flags': ['read']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0012': {
        'org.bluez.GattService1': {'UUID': 'e97dd91d-251d-470a-a062-fa1922dfa9a8',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0012/char0013': {
        'org.bluez.GattCharacteristic1': {'UUID': 'e97d3b10-251d-470a-a062-fa1922dfa9a8',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0012', 'Value': [],
                                          'Notifying': False, 'Flags': ['write-without-response', 'notify'],
                                          'WriteAcquired': False, 'NotifyAcquired': False}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0012/char0013/desc0015': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service0012/char0013',
                                      'Value': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service000e': {
        'org.bluez.GattService1': {'UUID': '0000fe59-0000-1000-8000-00805f9b34fb',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service000e/char000f': {
        'org.bluez.GattCharacteristic1': {'UUID': '8ec90004-f315-4f60-9fb8-838830daea50',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service000e', 'Value': [],
                                          'Notifying': False, 'Flags': ['write', 'indicate']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service000e/char000f/desc0011': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service000e/char000f',
                                      'Value': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service000a': {
        'org.bluez.GattService1': {'UUID': '00001801-0000-1000-8000-00805f9b34fb',
                                   'Device': '/org/bluez/hci0/dev_DD_02_02_02_02_02', 'Primary': True, 'Includes': []}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service000a/char000b': {
        'org.bluez.GattCharacteristic1': {'UUID': '00002a05-0000-1000-8000-00805f9b34fb',
                                          'Service': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service000a', 'Value': [],
                                          'Notifying': False, 'Flags': ['indicate']}},
    '/org/bluez/hci0/dev_DD_02_02_02_02_02/service000a/char000b/desc000d': {
        'org.bluez.GattDescriptor1': {'UUID': '00002902-0000-1000-8000-00805f9b34fb',
                                      'Characteristic': '/org/bluez/hci0/dev_DD_02_02_02_02_02/service000a/char000b',
                                      'Value': []}},

}
