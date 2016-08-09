import dbus
import dbus.mainloop.glib
from gi.repository import GLib

from bluezero import constants

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
mainloop = GLib.MainLoop()


def generic_error_cb(error):
    print('D-Bus call failed: ' + str(error))
    mainloop.quit()


class Service:
    def __init__(self, service_path):
        self.service_path = service_path
        self.bus = dbus.SystemBus()
        self.service_object = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.service_path)
        self.service_methods = dbus.Interface(self.service_object,
                                              constants.ADAPTER_INTERFACE)
        self.service_props = dbus.Interface(self.service_object,
                                            dbus.PROPERTIES_IFACE)

    def UUID(self):
        """
        Returns value of Service UUID for this path
        :return: string for example '00001800-0000-1000-8000-00805f9b34fb'
        """
        return self.service_props.Get(
            constants.GATT_SERVICE_IFACE, 'UUID')

    def device(self):
        """
        Returns the DBus object that this service belongs to
        :return: DBus object of device
        """
        return self.service_props.Get(
            constants.GATT_SERVICE_IFACE, 'Device')

    def Primary(self):
        """
        Returns a boolean saying if this a primary service
        :return: boolean
        """
        return self.service_props.Get(
            constants.GATT_SERVICE_IFACE, 'Primary')


class Characteristic:
    def __init__(self, characteristic_path):
        self.characteristic_path = characteristic_path
        self.bus = dbus.SystemBus()
        self.characteristic_object = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.characteristic_path)
        self.characteristic_methods = dbus.Interface(
            self.characteristic_object,
            constants.GATT_CHRC_IFACE)
        self.characteristic_props = dbus.Interface(
            self.characteristic_object,
            dbus.PROPERTIES_IFACE)

    def UUID(self):
        """
        Returns value of Characteristic UUID for this path
        :return: string example '00002a00-0000-1000-8000-00805f9b34fb'
        """
        return self.characteristic_props.Get(
            constants.GATT_CHRC_IFACE, 'UUID')

    def service(self):
        """
        Returns the DBus object for the service that this characteristic
        belongs to
        :return: DBus object of device
        """
        return self.characteristic_props.Get(
            constants.GATT_CHRC_IFACE, 'Service')

    def value(self):
        """
        The cached value of the characteristic. This property
        gets updated only after a successful read request and
        when a notification or indication is received, upon
        which a PropertiesChanged signal will be emitted.
        :return: DBus byte array
        """
        return self.characteristic_props.Get(
            constants.GATT_CHRC_IFACE, 'Value')

    def notifying(self):
        """
        Returns a boolean of if this characteristic has notifications enabled
        :return: Boolean
        """
        return self.characteristic_props.Get(
            constants.GATT_CHRC_IFACE, 'Notifying')

    def flags(self):
        """
        Returns a list of how this characteristic value can be used
        :return: list example ['read', 'write', 'notify']
        """
        return self.characteristic_props.Get(
            constants.GATT_CHRC_IFACE, 'Flags')

    def read_raw_value(self, flags=''):
        """
        Return the characteristic value if allowed
        :param flags: "offset": Start offset
                        "device": Device path (Server only)
        :return:

        Possible Errors:    org.bluez.Error.Failed
                            org.bluez.Error.InProgress
                            org.bluez.Error.NotPermitted
                            org.bluez.Error.InvalidValueLength
                            org.bluez.Error.NotAuthorized
                            org.bluez.Error.NotSupported
        """
        return self.characteristic_methods.ReadValue(dbus.Array())

    def write_value(self, value, flags=''):
        """
        Write a new value to the characteristic
        :param value:
        :param flags:
        :return:
        """
        self.characteristic_methods.WriteValue(value, dbus.Array(flags))

    def start_notify(self):
        self.characteristic_methods.StartNotify(
            reply_handler=self.start_notify_cb,
            error_handler=generic_error_cb,
            dbus_interface=constants.GATT_CHRC_IFACE)

    def stop_notify(self):
        self.characteristic_methods.StopNotify(
            reply_handler=self.stop_notify_cb,
            error_handler=generic_error_cb,
            dbus_interface=constants.GATT_CHRC_IFACE)

    def add_characteristic_cb(self, callback=None):
        if callback is None:
            callback = self.props_changed_cb

        self.characteristic_props.connect_to_signal('PropertiesChanged',
                                                    callback)

    def props_changed_cb(self, iface, changed_props, invalidated_props):
        if iface != constants.GATT_CHRC_IFACE:
            return

        if not len(changed_props):
            return

        value = changed_props.get('Value', None)
        if not value:
            return

        print('Properties changed: ', value)

    def start_notify_cb(self):
        print('Notifications enabled')

    def stop_notify_cb(self):
        print('Notifications disabled')


class Descriptor:
    def __init__(self, descriptor_path):
        self.descriptor_path = descriptor_path
        self.bus = dbus.SystemBus()
        self.descriptor_object = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.descriptor_path)
        self.descriptor_methods = dbus.Interface(self.descriptor_object,
                                                 constants.GATT_DESC_IFACE)
        self.descriptor_props = dbus.Interface(self.descriptor_object,
                                               dbus.PROPERTIES_IFACE)

    def UUID(self):
        """
        Returns value of Descriptor UUID for this path
        :return: string example '00002a00-0000-1000-8000-00805f9b34fb'
        """
        return self.descriptor_props.Get(
            constants.GATT_DESC_IFACE, 'UUID')

    def characteristic(self):
        """
        Object path of the GATT characteristic the descriptor
        belongs to
        :return: DBus object
        """
        return self.descriptor_props.Get(
            constants.GATT_DESC_IFACE, 'UUID')

    def value(self):
        """
        The cached value of the descriptor. This property
        gets updated only after a successful read request, upon
        which a PropertiesChanged signal will be emitted.
        :return: DBus byte array
        """
        return self.descriptor_props.Get(
            constants.GATT_CHRC_IFACE, 'Value')

    def flags(self):
        """
        Returns a list of how this descriptor value can be used
        :return: list example ['read', 'write']
        """
        return self.descriptor_props.Get(
            constants.GATT_CHRC_IFACE, 'Flags')

    def read_raw_value(self, flags=''):
        """
        Issues a request to read the value of the
        descriptor and returns the value if the
        operation was successful.

        :param flags: "offset": Start offset
                        "device": Device path (Server only)
        :return: dbus byte array
        """
        return self.descriptor_methods.ReadValue(dbus.Array(flags))

    def write_value(self, value, flags=''):
        """
        Issues a request to write the value of the descriptor
        :param value: DBus byte array
        :param flags: "offset": Start offset
                      "device": Device path (Server only)
        :return:
        """
        self.descriptor_methods.WriteValue(value, dbus.Array(flags))


class Profile:
    def __init__(self, profile_path):
        self.profile_path = profile_path
        self.bus = dbus.SystemBus()
        self.profile_object = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.profile_path)
        self.profile_methods = dbus.Interface(
            self.profile_object,
            constants.GATT_PROFILE_IFACE)
        self.profile_props = dbus.Interface(self.profile_object,
                                            dbus.PROPERTIES_IFACE)

    def release(self):
        """

        :return:
        """
        self.profile_methods.Release()

    def UUIDs(self):
        """128-bit GATT service UUIDs to auto connect.

        :return: list of UUIDs
        """
        return self.profile_props.Get(constants.GATT_PROFILE_IFACE, 'UUIDs')


class GattManager:
    def __init__(self, manager_path):
        self.manager_path = manager_path
        self.bus = dbus.SystemBus()
        self.manager_obj = self.bus.get_object(
            constants.BLUEZ_SERVICE_NAME,
            self.manager_path)
        self.manager_methods = dbus.Interface(
            self.manager_obj,
            constants.GATT_MANAGER_IFACE)
        self.manager_props = dbus.Interface(self.manager_obj,
                                            dbus.PROPERTIES_IFACE)

    def register_application(self, application, options):
        """

        :param application:
        :param options:
        :return:
        """
        self.manager_methods.RegisterApplication(
            application, options
        )

    def unregister_application(self, application):
        """

        :param application:
        :return:
        """
        self.manager_methods.UnregisterApplication(application)
