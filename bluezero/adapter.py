from __future__ import absolute_import, print_function, unicode_literals

import dbus
import dbus.mainloop.glib
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject
import bluezero.bluezutils as bluezutils

SERVICE_NAME = 'org.bluez'
ADAPTER_INTERFACE = SERVICE_NAME + '.Adapter1'

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


def list_adapters():
    paths = []
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object('org.bluez', '/'),
                             'org.freedesktop.DBus.ObjectManager')
    manager_obj = manager.GetManagedObjects()
    for path, ifaces in manager_obj.iteritems():
        adapter = ifaces.get(ADAPTER_INTERFACE)
        if adapter is None:
            continue
        else:
            obj = bus.get_object(SERVICE_NAME, path)
            paths.append(dbus.Interface(obj, ADAPTER_INTERFACE).object_path)
    if len(paths) < 1:
        raise Exception('No Bluetooth adapter found')
    else:
        return paths

compact = True
devices = {}


class Adapter:

    def __init__(self, dev_id=None):
        self.bus = dbus.SystemBus()
        self.dev_id = dev_id
        self.adapter_iface = bluezutils.find_adapter(dev_id)
        self.adapter_path = bluezutils.find_adapter(dev_id).object_path
        self.adapter = dbus.Interface(
            self.bus.get_object(
                'org.bluez',
                self.adapter_path),
            'org.freedesktop.DBus.Properties'
        )

    def address(self):
        addr = self.adapter.Get('org.bluez.Adapter1', 'Address')

        return addr

    def name(self):
        name = self.adapter.Get('org.bluez.Adapter1', 'Name')
        return name

    def alias(self, new_alias=None):
        if new_alias is None:
            alias = self.adapter.Get('org.bluez.Adapter1', 'Alias')
            return alias
        else:
            self.adapter.Set('org.bluez.Adapter1', 'Alias', new_alias)

    def list(self):
        adapters = {}
        om = dbus.Interface(self.bus.get_object('org.bluez', '/'),
                            'org.freedesktop.DBus.ObjectManager')
        objects = om.GetManagedObjects()
        for path, interfaces in objects.iteritems():
            if 'org.bluez.Adapter1' not in interfaces:
                continue

            # print(' [ %s ]' % (path))

            props = interfaces['org.bluez.Adapter1']

            for (key, value) in props.items():
                if key == 'Class':
                    print('    %s = 0x%06x' % (key, value))
                    adapters[key] = '0x%06x' % value
                else:
                    print('    %s = %s' % (key, value))
                    adapters[key] = '%s' % value
            # print('Returning')
            return adapters

    def powered(self, new_state=None):
        powered = ''
        if new_state is None:
            powered = self.adapter.Get('org.bluez.Adapter1', 'Powered')
        else:
            if new_state == 'on':
                value = dbus.Boolean(1)
            elif new_state == 'off':
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(new_state)
            self.adapter.Set('org.bluez.Adapter1', 'Powered', value)
            powered = self.adapter.Get('org.bluez.Adapter1', 'Powered')
        return powered

    def pairable(self, new_state=None):
        if new_state is None:
            pairable = self.adapter.Get('org.bluez.Adapter1', 'Pairable')
        else:
            if new_state == 'on':
                value = dbus.Boolean(1)
            elif new_state == 'off':
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(args[1])
            self.adapter.Set('org.bluez.Adapter1', 'Pairable', value)
            pairable = self.adapter.Get('org.bluez.Adapter1', 'Pairable')
        return pairable

    def pairabletimeout(self, new_to=None):
        if new_to is None:
            pt = self.adapter.Get('org.bluez.Adapter1', 'PairableTimeout')
        else:
            timeout = dbus.UInt32(new_to)
            self.adapter.Set('org.bluez.Adapter1', 'PairableTimeout', timeout)
        return pt

    def discoverable(self, new_state=None):
        if new_state is None:
            discoverable = self.adapter.Get('org.bluez.Adapter1',
                                            'Discoverable')
        else:
            if new_state == 'on':
                value = dbus.Boolean(1)
            elif new_state == 'off':
                value = dbus.Boolean(0)
            else:
                value = dbus.Boolean(args[1])
            self.adapter.Set('org.bluez.Adapter1', 'Discoverable', value)
            discoverable = self.adapter.Get('org.bluez.Adapter1',
                                            'Discoverable')
        return discoverable

    def discoverabletimeout(self, new_dt=None):
        if new_dt is None:
            dt = self.adapter.Get('org.bluez.Adapter1', 'DiscoverableTimeout')
        else:
            to = dbus.UInt32(new_dt)
            self.adapter.Set('org.bluez.Adapter1', 'DiscoverableTimeout', to)
            dt = self.adapter.Get('org.bluez.Adapter1', 'DiscoverableTimeout')
        return dt

    def discovering(self):
        discovering = self.adapter.Get('org.bluez.Adapter1', 'Discovering')
        return discovering

    @staticmethod
    def print_compact(address, properties):
        name = ''
        address = '<unknown>'

        for key, value in properties.iteritems():
            if type(value) is dbus.String:
                value = unicode(value).encode('ascii', 'replace')
            if key == 'Name':
                name = value
            elif key == 'Address':
                address = value

        if 'Logged' in properties:
            flag = '*'
        else:
            flag = ' '

        print('%s%s %s' % (flag, address, name))

        properties['Logged'] = True

    @staticmethod
    def print_normal(address, properties):
        print('[ ' + address + ' ]')

        for key in properties.keys():
            value = properties[key]
            if type(value) is dbus.String:
                value = unicode(value).encode('ascii', 'replace')
            if key == 'Class':
                print('    %s = 0x%06x' % (key, value))
            else:
                print('    %s = %s' % (key, value))

        print()

        properties['Logged'] = True

    @staticmethod
    def skip_dev(old_dev, new_dev):
        if 'Logged' not in old_dev:
            return False
        if 'Name' in old_dev:
            return True
        if 'Name' not in new_dev:
            return True
        return False

    def interfaces_added(self, path, interfaces):
        properties = interfaces['org.bluez.Device1']
        if not properties:
            return

        if path in devices:
            dev = devices[path]

            if compact and self.skip_dev(dev, properties):
                return
            devices[path] = dict(devices[path].items() + properties.items())
        else:
            devices[path] = properties

        if 'Address' in devices[path]:
            address = properties['Address']
        else:
            address = '<unknown>'

        if compact:
            self.print_compact(address, devices[path])
        else:
            self.print_normal(address, devices[path])

    def properties_changed(self, interface, changed, invalidated, path):
        if interface != 'org.bluez.Device1':
            return

        if path in devices:
            dev = devices[path]

            if compact and self.skip_dev(dev, changed):
                return
            devices[path] = dict(devices[path].items() + changed.items())
        else:
            devices[path] = changed

        if 'Address' in devices[path]:
            address = devices[path]['Address']
        else:
            address = '<unknown>'

        if compact:
            self.print_compact(address, devices[path])
        else:
            self.print_normal(address, devices[path])

    def start_scan(self):
        self.bus.add_signal_receiver(
            self.interfaces_added,
            dbus_interface='org.freedesktop.DBus.ObjectManager',
            signal_name='InterfacesAdded')

        self.bus.add_signal_receiver(
            self.properties_changed,
            dbus_interface='org.freedesktop.DBus.Properties',
            signal_name='PropertiesChanged',
            arg0='org.bluez.Device1',
            path_keyword='path')

        om = dbus.Interface(self.bus.get_object('org.bluez', '/'),
                            'org.freedesktop.DBus.ObjectManager')
        objects = om.GetManagedObjects()
        for path, interfaces in objects.iteritems():
            if 'org.bluez.Device1' in interfaces:
                devices[path] = interfaces['org.bluez.Device1']

        self.adapter_iface.StartDiscovery()

        mainloop = GObject.MainLoop()
        mainloop.run()

    def stop_scan(self):
        self.adapter_iface.StopDiscovery()
