"""Bluezero DBus mock template

This creates the expected methods and properties of the object manager
org.bluez object (/), the manager object (/org/bluez) for BlueZ 5 only.


This is based on the BLueZ5 template from:
https://github.com/martinpitt/python-dbusmock/

That had the following licensing information:
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.  See http://www.gnu.org/copyleft/lgpl.html for the full text
# of the license.

__author__ = 'Philip Withnall'
__email__ = 'philip.withnall@collabora.co.uk'
__copyright__ = '(c) 2013 Collabora Ltd.'
__license__ = 'LGPL 3+'
"""

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
DEVICE_IFACE = 'org.bluez.Device1'
SERVICE_IFACE = 'org.bluez.Service1'


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
        'Discoverable': dbus.Boolean(True, variant_level=1),
        'Discovering': dbus.Boolean(False, variant_level=1),
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
                       ('StartDiscovery',
                        '', '', 'self.mock_discovering(self)'),
                       ('StopDiscovery', '', '', ''),
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

    adapter.mock_discovering = mock_discovering
    manager = mockobject.objects['/']
    manager.EmitSignal(OBJECT_MANAGER_IFACE, 'InterfacesAdded',
                       'oa{sa{sv}}', [
                           dbus.ObjectPath(path),
                           {ADAPTER_IFACE: adapter_properties},
                       ])

    return path


def mock_discovering(self):
    self.Set(ADAPTER_IFACE, 'Discovering', dbus.Boolean(True, variant_level=1))


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
                     in_signature='sss', out_signature='s')
def AddService(self, adapter_device_name, device_address, alias):
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
    device_path = adapter_path + '/' + device_name
    path = device_path + '/service0001'

    if adapter_path not in mockobject.objects:
        raise dbus.exceptions.DBusException(
            'Adapter %s does not exist.' % adapter_device_name,
            name=BLUEZ_MOCK_IFACE + '.NoSuchAdapter')

    properties = {
        'UUID': dbus.String('180F', variant_level=1),
        'Primary': dbus.Boolean(True, variant_level=1),
        'Device': dbus.ObjectPath(device_name, variant_level=1),
    }

    self.AddObject(path,
                   SERVICE_IFACE,
                   # Properties
                   properties,
                   # Methods
                   [])

    manager = mockobject.objects['/']
    manager.EmitSignal(OBJECT_MANAGER_IFACE, 'InterfacesAdded',
                       'oa{sa{sv}}', [
                           dbus.ObjectPath(path),
                           {SERVICE_IFACE: properties},
                       ])

    return path


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='ss', out_signature='')
def PairDevice(self, adapter_device_name, device_address):
    """Convenience method to mark an existing device as paired.

    You have to specify a device address which must be a valid Bluetooth
    address (e.g. "AA:BB:CC:DD:EE:FF"). The adapter device name is the
    device_name passed to AddAdapter.

    This unblocks the device if it was blocked.

    If the specified adapter or device do not exist, a NoSuchAdapter or
    NoSuchDevice error will be returned on the bus.

    Returns nothing.
    """
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
            'Class': dbus.UInt32(5898764, variant_level=1),
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
            'Class': dbus.UInt32(5898764, variant_level=1),
            'Icon': dbus.String('phone', variant_level=1),
        },
        [],
    ])


@dbus.service.method(BLUEZ_MOCK_IFACE,
                     in_signature='ss', out_signature='')
def BlockDevice(self, adapter_device_name, device_address):
    """Convenience method to mark an existing device as blocked.

    You have to specify a device address which must be a valid Bluetooth
    address (e.g. 'AA:BB:CC:DD:EE:FF'). The adapter device name is the
    device_name passed to AddAdapter.

    This disconnects the device if it was connected.

    If the specified adapter or device do not exist, a NoSuchAdapter or
    NoSuchDevice error will be returned on the bus.

    Returns nothing.
    """
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
                     in_signature='', out_signature='')
def ConnectDevice(self):
    """Convenience method to mark an existing device as connected.

    You have to specify a device address which must be a valid Bluetooth
    address (e.g. 'AA:BB:CC:DD:EE:FF'). The adapter device name is the
    device_name passed to AddAdapter.

    This unblocks the device if it was blocked.

    If the specified adapter or device do not exist, a NoSuchAdapter or
    NoSuchDevice error will be returned on the bus.

    Returns nothing.
    """
    device_name = 'dev_' + '11:22:33:44:55:66'.replace(':', '_').upper()
    adapter_path = '/org/bluez/' + 'hci0'
    device_path = adapter_path + '/' + device_name
    # print('xxxx', adapter_path)
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
    """Convenience method to mark an existing device as disconnected.

    You have to specify a device address which must be a valid Bluetooth
    address (e.g. "AA:BB:CC:DD:EE:FF"). The adapter device name is the
    device_name passed to AddAdapter.

    This does not change the devices blocked status.

    If the specified adapter or device do not exist, a NoSuchAdapter or
    NoSuchDevice error will be returned on the bus.

    Returns nothing.
    """
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
