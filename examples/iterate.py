import dbus
from xml.etree import ElementTree


DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

BLUEZ_DEVICE_IFACE = 'org.bluez.Device1'
BLUEZ_SERVICE_NAME = 'org.bluez'
BLUEZ_SRVC_IFACE = 'org.bluez.GattService1'
BLUEZ_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
BLUEZ_DSCR_IFACE = 'org.bluez.GattDescriptor1'

bus = dbus.SystemBus()


class BluezClass:
    devices = {}

    @classmethod
    def get_device(cls, path):
        for dev in cls.devices.keys():
            if cls.devices[dev].dev_path in path:
                return cls.devices[dev]

    def __init__(self, path, address, name, alias, adapter, uuids):
        BluezClass.devices[address] = self
        self.dev_path = path
        self.address = address
        self.name = name
        self.alias = alias
        self.adapter = adapter
        self.uuids = uuids
        self.services = {}
        self.characteristics = {}
        self.descriptors = {}

    def add_service_path(self, service_uuid, service_path):
        self.services[service_uuid] = service_path

    def add_characteristic_path(self, char_uuid, char_path):
        self.characteristics[char_uuid] = char_path

    def add_descriptor_path(self, descr_uuid, descr_path):
        self.descriptors[descr_uuid] = descr_path

    def get_characteristics_for_service(self, srvc_path):
        service_chars = {}
        for char in self.characteristics.keys():
            if srvc_path in self.characteristics[char]:
                service_chars[char] = self.characteristics[char]

        return service_chars

    def get_descriptors_for_characteristic(self, chrc_path):
        char_descr = {}
        for descr in self.descriptors.keys():
            if chrc_path in descr:
                char_descr[descr] = self.descriptors[descr]

        return char_descr


def get_prop(object_path, prop_name, iface):
        props_iface = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, object_path),
            DBUS_PROP_IFACE)
        prop_value = props_iface.Get(iface, prop_name)

        return prop_value


def build_introspection(bus_type, service, object_path):
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
            build_introspection(bus_type, service, new_path)
        if child.tag == 'interface':
            if child.attrib['name'] == BLUEZ_DEVICE_IFACE:
                dev_address = get_prop(object_path,
                                       'Address',
                                       BLUEZ_DEVICE_IFACE)
                dev_name = get_prop(object_path,
                                    'Name',
                                    BLUEZ_DEVICE_IFACE)
                dev_alias = get_prop(object_path,
                                     'Alias',
                                     BLUEZ_DEVICE_IFACE)
                dev_adapter = get_prop(object_path,
                                       'Adapter',
                                       BLUEZ_DEVICE_IFACE)
                dev_uuids = get_prop(object_path,
                                     'UUIDs',
                                     BLUEZ_DEVICE_IFACE)
                BluezClass(object_path,
                           dev_address,
                           dev_name,
                           dev_alias,
                           dev_adapter,
                           dev_uuids)
                # print('Device address: {}'.format(dev_address))
            if child.attrib['name'] == BLUEZ_SRVC_IFACE:
                service_uuid = get_prop(object_path, 'UUID', BLUEZ_SRVC_IFACE)
                service_dev = get_prop(object_path, 'Device', BLUEZ_SRVC_IFACE)
                service_primary = get_prop(object_path,
                                           'Primary',
                                           BLUEZ_SRVC_IFACE)
                ubit_obj = BluezClass.get_device(service_dev)
                ubit_obj.add_service_path(str(service_uuid), object_path)
            if child.attrib['name'] == BLUEZ_CHRC_IFACE:
                char_uuid = get_prop(object_path, 'UUID', BLUEZ_CHRC_IFACE)
                parent_srvc_path = get_prop(object_path,
                                            'Service',
                                            BLUEZ_CHRC_IFACE)
                ubit_obj = BluezClass.get_device(parent_srvc_path)
                ubit_obj.add_characteristic_path(str(char_uuid), object_path)
            if child.attrib['name'] == BLUEZ_DSCR_IFACE:
                dscr_uuid = get_prop(object_path, 'UUID', BLUEZ_DSCR_IFACE)
                ubit_obj = BluezClass.get_device(object_path)
                ubit_obj.add_descriptor_path(object_path, str(dscr_uuid))


def get_path_for_uuid(address, uuid, attribute_type):
    bluez_dev = BluezClass.devices[address.upper()]
    if attribute_type == 'service':
        return bluez_dev.services[uuid.lower()]
    elif attribute_type == 'characteristic':
        return bluez_dev.characteristics[uuid.lower()]
    else:
        return None


def get_path_for_device(address):
    for addr in BluezClass.devices.keys():
        if BluezClass.devices[addr].address.lower() == address.lower():
            return BluezClass.devices[addr].dev_path
    return None


if __name__ == '__main__':
    build_introspection(bus, 'org.bluez', '/org/bluez/hci0')
    for addr in BluezClass.devices.keys():
        print('Device Name: ', BluezClass.devices[addr].name)
        print('Device Address: ', BluezClass.devices[addr].address)
        print('Device Adapter: ', BluezClass.devices[addr].adapter)
        bz_dev = BluezClass.devices[addr]
        for uuid in bz_dev.uuids:
            if uuid in bz_dev.services:
                print('\t{} at {}'.format(
                    uuid,
                    bz_dev.services[str(uuid)]))
                for chrc in bz_dev.get_characteristics_for_service(
                        bz_dev.services[str(uuid)]).keys():
                    print('\t\t{} at {}'.format(
                        chrc,
                        bz_dev.characteristics[chrc]))
                    for dscr in bz_dev.get_descriptors_for_characteristic(
                            bz_dev.characteristics[chrc]).keys():
                        print('\t\t\t{} at {}'.format(
                            bz_dev.descriptors[dscr], dscr))
