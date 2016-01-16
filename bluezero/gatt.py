import sys

import dbus
import dbus.service
import dbus.mainloop.glib

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

from dbus.mainloop.glib import DBusGMainLoop

bus = None
mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'

KEYS_SVC_UUID = '0000180f-0000-1000-8000-00805f9b34fb'
KEYS_CHR_UUID = '00002a19-0000-1000-8000-00805f9b34fb'

BAT_SVC_UUID = '0000180F-0000-1000-8000-00805f9b34fb'
BAT_CHR_UUID = '00002A19-0000-1000-8000-00805f9b34fb'

# The objects that we interact with.
keys_service = None


class Client:
    def __init__(self, dev_path):
        # Set up the main loop.
        DBusGMainLoop(set_as_default=True)
        global bus
        bus = dbus.SystemBus()
        global mainloop
        mainloop = GObject.MainLoop()

        self.bat_level = None

        self.om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                 DBUS_OM_IFACE)
        self.om.connect_to_signal('InterfacesRemoved',
                                  self.interfaces_removed_cb)

        service_path = dev_path + '/service0028'
        print('Service Path: {}'.format(service_path))

        try:
            if not self.process_keys_service(service_path):
                sys.exit(1)
        except dbus.DBusException as e:
            print(e.message)
            sys.exit(1)

        print('Keys Service ready')

        self.start_client()

        try:
            mainloop.run()
        except (KeyboardInterrupt, SystemExit):
            mainloop.quit()

    @classmethod
    def generic_error_cb(error):
        print('D-Bus call failed: ' + str(error))
        mainloop.quit()

    def keys_msrmt_start_notify_cb(self):
        print('Keys notifications enabled')

    def keys_msrmt_changed_cb(self, iface, changed_props, invalidated_props):
        if iface != GATT_CHRC_IFACE:
            return

        if not len(changed_props):
            return

        value = changed_props.get('Value', None)
        if not value:
            return

        print('Battery Change')

        flags = value[0]

        print('\tCharge: ' + str(int(flags)))
        self.bat_level = str(int(flags))

    def start_client(self):
        # Listen to PropertiesChanged signals from the Keys
        # Characteristic.
        keys_msrmt_prop_iface = dbus.Interface(keys_msrmt_chrc[0],
                                               DBUS_PROP_IFACE)
        keys_msrmt_prop_iface.connect_to_signal("PropertiesChanged",
                                                self.keys_msrmt_changed_cb)

        # Subscribe to Heart Rate Measurement notifications.
        keys_msrmt_chrc[0].StartNotify(
            reply_handler=self.keys_msrmt_start_notify_cb,
            error_handler=Client.generic_error_cb,
            dbus_interface=GATT_CHRC_IFACE)

    def process_chrc(self, chrc_path):
        chrc = bus.get_object(BLUEZ_SERVICE_NAME, chrc_path)
        chrc_props = chrc.GetAll(GATT_CHRC_IFACE,
                                 dbus_interface=DBUS_PROP_IFACE)

        uuid = chrc_props['UUID']
        print('Processing chrc: {}'.format(uuid))

        if uuid == KEYS_CHR_UUID:
            global keys_msrmt_chrc
            keys_msrmt_chrc = (chrc, chrc_props)
        else:
            print('Unrecognized characteristic: ' + uuid)

        return True

    def process_keys_service(self, service_path):
        service = bus.get_object(BLUEZ_SERVICE_NAME, service_path)
        service_props = service.GetAll(GATT_SERVICE_IFACE,
                                       dbus_interface=DBUS_PROP_IFACE)

        uuid = service_props['UUID']
        print(str(uuid), KEYS_SVC_UUID)

        if uuid != KEYS_SVC_UUID:
            print('Service is not a Keys Service: ' + uuid)
            return False

        # Process the characteristics.
        chrc_paths = service_props['Characteristics']
        for chrc_path in chrc_paths:
            print('Char path {}'.format(chrc_path))
            self.process_chrc(chrc_path)

        global keys_service
        keys_service = (service, service_props, service_path)

        return True

    def interfaces_removed_cb(self, object_path, interfaces):
        if not keys_service:
            return

        if object_path == keys_service[2]:
            print('Service was removed')
            mainloop.quit()


if __name__ == '__main__':
    Client('/org/bluez/hci0/dev_7F_0D_31_10_90_32')
