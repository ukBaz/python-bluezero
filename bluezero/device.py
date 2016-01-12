
from __future__ import absolute_import, print_function, unicode_literals

import sys
from time import sleep
import threading
import dbus
import dbus.mainloop.glib
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject
import bluezero.bluezutils as bluezutils


class Device:
    def __init__(self, adapter_obj=None):
        self.devices = {}
        self.dev_addr = None
        self.dev_path = None
        self.device = None
        self.compact = False
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.mainloop = GObject.MainLoop()
        if adapter_obj is None:
            self.adapter = bluezutils.find_adapter()
            self.adapter_path = bluezutils.find_adapter().object_path
        else:
            self.adapter = adapter_obj.adapter_iface
            self.adapter_path = adapter_obj.adapter_path
            self.dev_id = adapter_obj.dev_id
        self.services = None

    def list(self):
        om = dbus.Interface(self.bus.get_object("org.bluez", "/"),
                            "org.freedesktop.DBus.ObjectManager")
        objects = om.GetManagedObjects()

        for path, interfaces in objects.iteritems():
            if "org.bluez.Device1" not in interfaces:
                continue
            properties = interfaces["org.bluez.Device1"]
            if properties["Adapter"] != self.adapter_path:
                continue
            print("%s %s" % (properties["Address"], properties["Alias"]))
            self.devices[properties["Address"]] = properties["Alias"]

    def create_device_reply(self, device):
        print("New device (%s)" % device)
        self.mainloop.quit()
        sys.exit(0)

    def create_device_error(self, error):
        print("Creating device failed: %s" % error)
        self.mainloop.quit()
        sys.exit(1)

    def create(self, address=None):
        if address is None:
            print("Need address parameter")
        else:
            self.adapter.CreateDevice(address,
                                      reply_handler=self.create_device_reply,
                                      error_handler=self.create_device_error)
        self.mainloop.run()

    def remove(self, address):
        if address is None:
            print("Need address or object path parameter")
        else:
            managed_objects = bluezutils.get_managed_objects()
            try:
                dev = bluezutils.find_device_in_objects(managed_objects,
                                                        address,
                                                        self.dev_id)
                path = dev.object_path
            except:
                path = address
            self.adapter.RemoveDevice(path)

    def connect(self, address=None, profile=None):
        if address is None:
            print("Need address parameter")
        else:
            self.device = bluezutils.find_device(address, self.adapter_path)
            # print('Device: {0}'.format(device))
            if profile is None:
                self.device.Connect()
            else:
                self.device.ConnectProfile(profile)

    def disconnect(self):
        self.device.Disconnect()

    def uuid(self, address=None):
        if address is None:
            print("Need address parameter")
        else:
            device = bluezutils.find_device(address, self.dev_id)
            path = device.object_path
            print('Path to object: {}'.format(path))
            props = dbus.Interface(self.bus.get_object("org.bluez", path),
                                   "org.freedesktop.DBus.Properties")
            cls = props.Get("org.bluez.Device1", "Class")
            print("0x{0}".format(cls))

    def name(self, address):
        if address is None:
            print("Need address parameter")
        else:
            device = bluezutils.find_device(address, self.dev_id)
            path = device.object_path
            props = dbus.Interface(self.bus.get_object("org.bluez", path),
                                   "org.freedesktop.DBus.Properties")
            name = props.Get("org.bluez.Device1", "Name")
            return name

    def alias(self, address=None, alias_name=None):
        if address is None:
            print("Need address parameter")
        else:
            device = bluezutils.find_device(address, self.dev_id)
            path = device.object_path
            props = dbus.Interface(self.bus.get_object("org.bluez", path),
                                   "org.freedesktop.DBus.Properties")
            if alias_name is None:
                alias = props.Get("org.bluez.Device1", "Alias")
                return alias
            else:
                props.Set("org.bluez.Device1", "Alias", alias_name)

    def trusted(self, address=None, state=None):
        if address is None:
            print("Need address parameter")
        else:
            device = bluezutils.find_device(address, self.dev_id)
            path = device.object_path
            props = dbus.Interface(self.bus.get_object("org.bluez", path),
                                   "org.freedesktop.DBus.Properties")
            if state is None:
                trusted = props.Get("org.bluez.Device1", "Trusted")
                return trusted
            else:
                if state == "yes":
                    value = dbus.Boolean(1)
                elif state == "no":
                    value = dbus.Boolean(0)
                else:
                    value = dbus.Boolean(state)
                props.Set("org.bluez.Device1", "Trusted", value)

    def blocked(self, address=None, state=None):
        if address is None:
            print("Need address parameter")
        else:
            path = self.device.object_path
            props = dbus.Interface(self.bus.get_object("org.bluez", path),
                                   "org.freedesktop.DBus.Properties")
            if state is None:
                blocked = props.Get("org.bluez.Device1", "Blocked")
                return blocked
            else:
                if state == "yes":
                    value = dbus.Boolean(1)
                elif state == "no":
                    value = dbus.Boolean(0)
                else:
                    value = dbus.Boolean(state)
                props.Set("org.bluez.Device1", "Blocked", value)

    def connected(self):
        if self.device is None:
            conn_state = False
        else:
            path = self.device.object_path
            props = dbus.Interface(self.bus.get_object("org.bluez", path),
                                   "org.freedesktop.DBus.Properties")
            conn_state = props.Get("org.bluez.Device1", "Connected")

        return conn_state

    def request_device(self, name=None, alias=None, service=None):
        self.bus.add_signal_receiver(self.interfaces_added,
                                     dbus_interface = "org.freedesktop.DBus.ObjectManager",
                                     signal_name = "InterfacesAdded")

        self.bus.add_signal_receiver(self.properties_changed,
                                     dbus_interface = "org.freedesktop.DBus.Properties",
                                     signal_name = "PropertiesChanged",
                                     arg0 = "org.bluez.Device1",
                                     path_keyword = "path")

        self.bus.add_signal_receiver(self.property_changed,
                                     dbus_interface = "org.bluez.Adapter1",
                                     signal_name = "PropertyChanged")

        # self.list()

        self.adapter.StartDiscovery()

        try:
            run_event = threading.Event()
            run_event.set()
            thread_obj = threading.Thread(target=self.request_device_cb, args=(run_event,name, service,))
            thread_obj.start()
            self.mainloop.run()
            thread_obj.join()
        except (KeyboardInterrupt, SystemExit):
            self.mainloop.quit()
            run_event.clear()
            thread_obj.join()
            self.adapter.StopDiscovery()

    def request_device_cb(self, run_event, name, service):
        while run_event.is_set():
            for device in self.devices:
                if 'Name' in self.devices[device].keys():
                    print(name)
                    if name in str(self.devices[device]['Name']):
                        print(service)
                        for UUID in self.devices[device]['UUIDs']:
                            if service in str(UUID):
                                print('  ****  We have a match!!!  ***')
                                print()
                                print('Device Address: {}'.format(self.devices[device]['Address']))
                                self.dev_addr = str(self.devices[device]['Address'])
                                self.dev_path = str(device)
                                print('Device Name: {}'.format(self.devices[device]['Name']))
                                print('Device UUIDs: {}'.format(UUID))
                                run_event.clear()
                                self.mainloop.quit()
                                self.adapter.StopDiscovery()
            sleep(1)
        print('Thread: exit')
        return



    def print_compact(self, address, properties):
        # print('DEBUG: print_compact')
        name = ""
        address = "<unknown>"

        for key, value in properties.iteritems():
            if type(value) is dbus.String:
                value = unicode(value).encode('ascii', 'replace')
            if (key == "Name"):
                name = value
            elif (key == "Address"):
                address = value

        if "Logged" in properties:
            flag = "*"
        else:
            flag = " "

        # print("%s%s %s" % (flag, address, name))

        properties["Logged"] = True

    def print_normal(self, address, properties):
        # print('DEBUG: print_normal')
        # print("[ " + address + " ]")

        for key in properties.keys():
            value = properties[key]
            if type(value) is dbus.String:
                value = unicode(value).encode('ascii', 'replace')
            """
            if (key == "Class"):
                print("    %s = 0x%06x" % (key, value))
            else:
                print("    %s = %s" % (key, value))
            """

        # print()

        properties["Logged"] = True

    def skip_dev(self, old_dev, new_dev):
        if "Logged" not in old_dev:
            return False
        if "Name" in old_dev:
            return True
        if "Name" not in new_dev:
            return True
        return False

    def interfaces_added(self, path, interfaces):
        # print('DEBUG: interfaces_added')
        properties = interfaces["org.bluez.Device1"]
        if not properties:
            return

        if path in self.devices:
            dev = self.devices[path]

            if self.compact and self.skip_dev(dev, properties):
                return
            self.devices[path] = dict(self.devices[path].items() + properties.items())
        else:
            self.devices[path] = properties

        if "Address" in self.devices[path]:
            address = properties["Address"]
        else:
            address = "<unknown>"

        if self.compact:
            self.print_compact(address, self.devices[path])
        else:
            self.print_normal(address, self.devices[path])

    def properties_changed(self, interface, changed, invalidated, path):
        # print('DEBUG: properties_changed')
        if interface != "org.bluez.Device1":
            return

        if path in self.devices:
            dev = self.devices[path]

            if self.compact and self.skip_dev(dev, changed):
                return
            self.devices[path] = dict(self.devices[path].items() + changed.items())
        else:
            self.devices[path] = changed

        if "Address" in self.devices[path]:
            address = self.devices[path]["Address"]
        else:
            address = "<unknown>"

        if self.compact:
            self.print_compact(address, self.devices[path])
        else:
            self.print_normal(address, self.devices[path])

    def property_changed(self, name, value):
        # print('DEBUG: property_changed')
        if (name == "Discovering" and not value):
            self.mainloop.quit()

    def list_services(self):
        pass
