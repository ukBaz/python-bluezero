import dbus
from xml.etree import ElementTree

BLUEZ_SERVICE_NAME = 'org.bluez'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
CHAR_IFACE = 'org.bluez.GattCharacteristic1'

bus = dbus.SystemBus()


def print_introspection(bus_type, service, object_path):
    obj = bus_type.get_object(service, object_path)
    iface = dbus.Interface(obj, dbus.INTROSPECTABLE_IFACE)
    xml_string = iface.Introspect()
    # print (xml_string)
    for child in ElementTree.fromstring(xml_string):
        # print(child.tag, child.attrib)
        if child.tag == 'node':
            if object_path == '/':
                object_path = ''
            new_path = '/'.join((object_path, child.attrib['name']))
            # print(new_path)
            print_introspection(bus_type, service, new_path)
        if child.tag == 'interface':
            if child.attrib['name'] == CHAR_IFACE:
                # print('--> ', child.attrib['name'])
                char_props = dbus.Interface(
                    bus_type.get_object(BLUEZ_SERVICE_NAME, object_path),
                    DBUS_PROP_IFACE)
                # Read UUID property
                fetch_prop = 'UUID'
                service_data = char_props.Get(CHAR_IFACE, fetch_prop)
                print('UUID: {0}  -  Path: {1} '.format(
                    service_data, object_path))


print_introspection(bus, 'org.bluez', '/org/bluez/hci0')
