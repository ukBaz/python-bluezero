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
    lea_mngr_properties = {
        'ActiveInstances': dbus.Byte(1),
        'SupportedIncludes': dbus.Array(["appearance", "local-name"], signature='s'),
        'SupportedInstances': dbus.Byte(4),
    }
    self.AddProperties(LEDADVERTISING_MNGR_IFACE,
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
                       'oa{sa{sv}}', [
                           dbus.ObjectPath(path),
                           {ADAPTER_IFACE: adapter_properties,
                            LEDADVERTISING_MNGR_IFACE: lea_mngr_properties}
                       ])

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
                       ('Connect', '', '', ''),
                       ('ConnectProfile', 's', '', ''),
                       ('Disconnect', '', '', ''),
                       ('DisconnectProfile', 's', '', ''),
                       ('Pair', '', '', ''),
                   ])

    manager = mockobject.objects['/']
    manager.EmitSignal(OBJECT_MANAGER_IFACE, 'InterfacesAdded',
                       'oa{sa{sv}}', [
                           dbus.ObjectPath(path),
                           {DEVICE_IFACE: properties},
                       ])

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

    device.EmitSignal(dbus.PROPERTIES_IFACE, 'PropertiesChanged', 'sa{sv}as', [
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
    ])


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

    device.EmitSignal(dbus.PROPERTIES_IFACE, 'PropertiesChanged', 'sa{sv}as', [
        DEVICE_IFACE,
        {
            'Blocked': dbus.Boolean(True, variant_level=1),
            'Connected': dbus.Boolean(False, variant_level=1),
        },
        [],
    ])


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

    device.EmitSignal(dbus.PROPERTIES_IFACE, 'PropertiesChanged', 'sa{sv}as', [
        DEVICE_IFACE,
        {
            'Blocked': dbus.Boolean(False, variant_level=1),
            'Connected': dbus.Boolean(True, variant_level=1),
        },
        [],
    ])


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

    device.EmitSignal(dbus.PROPERTIES_IFACE, 'PropertiesChanged', 'sa{sv}as', [
        DEVICE_IFACE,
        {
            'Connected': dbus.Boolean(False, variant_level=1),
        },
        [],
    ])


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
                       ('Connect', '', '', ''),
                       ('ConnectProfile', 's', '', ''),
                       ('Disconnect', '', '', ''),
                       ('DisconnectProfile', 's', '', ''),
                       ('Pair', '', '', ''),
                   ])

    manager = mockobject.objects['/']
    manager.EmitSignal(OBJECT_MANAGER_IFACE, 'InterfacesAdded',
                       'oa{sa{sv}}', [
                           dbus.ObjectPath(path),
                           {DEVICE_IFACE: properties},
                       ])


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='', out_signature='')
def DeviceDiscovery(self):
    # Eddystone URL Beacon
    self.AddBeacon('hci0', '11:22:33:44:55:66',
                   service_uuid='0000feaa-0000-1000-8000-00805f9b34fb',
                   service_data=[16, 8, 1, 98, 108, 117, 101, 116, 111,
                                 111, 116, 104, 7])
    # Eddystone UID Beacon
    self.AddBeacon('hci0', '11:22:33:44:55:99',
                   service_uuid='0000feaa-0000-1000-8000-00805f9b34fb',
                   service_data=[0, 191, 0, 0, 0, 0, 0, 69, 97, 114, 116, 104,
                                 0, 0, 0, 0, 0, 11])
    # AltBeacon
    self.AddBeacon('hci0', '11:22:33:44:55:77',
                   manf_id=65535,
                   manf_data=[190, 172, 72, 37, 62, 89, 114, 36, 68, 99,
                              185, 184, 3, 63, 250, 181, 202, 254, 97, 99,
                              101, 107, 188, 0])
    # iBeacon
    self.AddBeacon('hci0', '11:22:33:44:55:88',
                   manf_id=76,
                   manf_data=[2, 21, 106, 177, 124, 23, 244, 123, 77, 65, 128,
                              54, 82, 106, 238, 210, 47, 115, 1, 22, 3, 104,
                              191])
