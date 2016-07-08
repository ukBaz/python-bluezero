import dbus
from xml.etree import ElementTree

bus = dbus.SystemBus()


def print_introspection(bus_type, service, object_path):
    obj = bus_type.get_object(service, object_path)
    iface = dbus.Interface(obj, dbus.INTROSPECTABLE_IFACE)
    xml_string = iface.Introspect()
    print(xml_string)
    for child in ElementTree.fromstring(xml_string):
        if child.tag == 'node':
            if object_path == '/':
                object_path = ''
            new_path = '/'.join((object_path, child.attrib['name']))
            print_introspection(bus_type, service, new_path)

print_introspection(bus, 'ukBaz.bluezero', '/')
