"""
Utility file to assist with using Gio.DBus* functionality.
"""
import logging

from gi.repository import Gio, GLib, GObject
import re

from bluezero import constants
from bluezero import tools

logger = tools.create_module_logger(__name__)


class BluezMethod:
    """
    This is allow BlueZ DBus methods to be discoverable in Python through
    introspection and be called from the proxy object
    """
    def __init__(self, method_name, method_proxy, in_args, out_args):
        self.in_args = f"({''.join(arg.signature for arg in in_args)})"
        self.out_args = f"({''.join([arg.signature for arg in out_args])})"
        self.method_proxy = method_proxy
        self.method_name = method_name

    def __call__(self, *args, **kwargs):
        # Example raw call
        # method_proxy.SetDiscoveryFilter('(a{sv})',
        #                           {'DuplicateData': GLib.Variant('b', True)})

        arg_variant = GLib.Variant(self.in_args, tuple(args))
        result = self.method_proxy.call_sync(
            self.method_name, arg_variant, kwargs.get('flags', 0),
            kwargs.get('timeout', -1), None)
        return self._unpack_result(result)

    @staticmethod
    def _unpack_result(result):
        """Convert a D-BUS return variant into an appropriate return value"""

        result = result.unpack()

        # to be compatible with standard Python behaviour, unbox
        # single-element tuples and return None for empty result tuples
        if len(result) == 1:
            result = result[0]
        elif len(result) == 0:
            result = None

        return result


class BluezProperty:
    """
    This is allow BlueZ DBus properties to be discoverable in Python through
    introspection and be called from the proxy object

    """
    def __init__(self, property_name, property_proxy,
                 property_info, bluez_iface):
        self.prop_proxy = property_proxy
        self._prop_name = property_name
        self.bluez_iface = bluez_iface
        # print('\tproperty name', property_name, property_info.signature)
        self.in_args = f"({property_info.signature})"

    def __get__(self, instance, owner=None):
        # Example get
        # props_proxy.Get('(ss)', ADAPTER, 'Powered')
        # print('get prop', instance, '-', owner)
        return self.prop_proxy.Get(
            '(ss)', self.bluez_iface, self._prop_name)

    def __set__(self, instance, value):
        self.prop_proxy.Set(
            '(ssv)', self.bluez_iface, self._prop_name, value)


class BluezSignal:
    def __init__(self, connection, signal_name, object_path):
        self._signal_proxy = connection
        self._sig_name = signal_name
        self._obj_path = object_path
        self.callback = None

    def __get__(self, instance, owner):
        return self.callback

    def __set__(self, instance, value):
        print('update value', value)
        self.callback = value

        # def signal_trigger(sender, object, iface, signal, params):
        #     self.callback(*params)

        instance._signal_proxy.connect('g-properties-changed', value)


def delete_me(arg1, arg2, arg3):
    print('Callback working', arg1, arg2, arg3)


def BluezDBusObject(object_path, bluez_iface):
    """
    Returns a proxy instance for the specified BlueZ object path and interface
    """
    class BluezProxy:
        pass

    _client = Gio.DBusObjectManagerClient.new_for_bus_sync(
        bus_type=Gio.BusType.SYSTEM,
        flags=Gio.DBusObjectManagerClientFlags.NONE,
        name='org.bluez',
        object_path='/',
        get_proxy_type_func=None,
        get_proxy_type_user_data=None,
        cancellable=None,
    )
    _conn = _client.get_connection()
    _method = {}
    _property = {}
    _signal = {}
    _object = _client.get_object(object_path)
    _intro_proxy = _object.get_interface(constants.DBUS_INTROSPECT_IFACE)
    prop_proxy = _object.get_interface(constants.DBUS_PROP_IFACE)
    method_proxy = _object.get_interface(bluez_iface)
    proxy_xml = introspection(_intro_proxy)
    for method in proxy_xml.get(bluez_iface).methods:
        _method[method.name] = BluezMethod(
            method.name, method_proxy, method.in_args, method.out_args)
        setattr(BluezProxy, method.name, _method[method.name])
    for prop_name in method_proxy.get_cached_property_names():
        prop_info = proxy_xml.get(bluez_iface).lookup_property(prop_name)
        _property[prop_name] = BluezProperty(
            prop_name, prop_proxy, prop_info, bluez_iface)
        setattr(BluezProxy, prop_name, _property[prop_name])
    for sig in proxy_xml.get(constants.DBUS_PROP_IFACE).signals:
        print(sig.name)
        # create on<SignalName> to store callback name
        # Connect function that checks for if on<SignalName> is set to value

    signal_proxy = Gio.DBusProxy.new_for_bus_sync(
        Gio.BusType.SYSTEM,
        Gio.DBusProxyFlags.NONE,
        None,
        "org.bluez",
        object_path,
        bluez_iface)
    # for prop_signal in proxy_xml.get(constants.DBUS_PROP_IFACE).signals:
    #     print(f'found {prop_signal.name} {object_path} {[arg.name for arg in prop_signal.args]}')
    #     _signal[prop_signal.name] = BluezSignal(
    #         signal_proxy, prop_signal.name, object_path)
    #     setattr(BluezProxy, f'on{prop_signal.name}', _signal[prop_signal.name])
    #     # prop_proxy.connect('g-properties-changed', delete_me)
    setattr(BluezProxy, 'signals', signal_proxy)
    return BluezProxy


def introspection(_intro_proxy):
    """
    Get node information from D-Bus introspection
    """
    node_data = {}
    xml_txt = _intro_proxy.Introspect()
    # print(xml_txt)
    node_info = Gio.DBusNodeInfo.new_for_xml(xml_txt).interfaces
    for node_iface in node_info:
        node_data[node_iface.name] = node_iface
    return node_data


def _build_variant(iface, name, signature, py_value):
    if all((iface == constants.LE_ADVERTISEMENT_IFACE,
            name == 'ServiceData')):
        s_data = GLib.VariantDict.new()
        for key, value in py_value.items():
            gvalue = GLib.Variant('ay', value)
            s_data.insert_value(key, gvalue)
        return s_data.end()


def get_managed_objects():
    return Gio.DBusProxy.new_for_bus_sync(
            bus_type=Gio.BusType.SYSTEM,
            flags=Gio.DBusProxyFlags.NONE,
            info=None,
            name='org.bluez',
            object_path='/',
            interface_name='org.freedesktop.DBus.ObjectManager',
            cancellable=None).GetManagedObjects()


def _get_dbus_path2(objects, parent_path, iface_in, prop, value):
    """
    Find DBus path for given DBus interface with property of a given value.

    :param objects: Dictionary of objects to search
    :param parent_path: Parent path to include in search
    :param iface_in: The interface of interest
    :param prop: The property to search for
    :param value: The value of the property being searched for
    :return: Path of object searched for
    """
    if parent_path is None:
        return None
    for path, iface in objects.items():
        props = iface.get(iface_in)
        if props is None:
            continue
        dev_name = "dev_" + value.lower().replace(":", "_")
        if (props[prop].lower() == value.lower() or
            path.lower().endswith(dev_name)) \
                and path.startswith(parent_path):
            return path
    return None


def get_dbus_path(adapter=None,
                  device=None,
                  service=None,
                  characteristic=None,
                  descriptor=None):
    """
    Return a DBus path for the given properties
    :param adapter: Adapter address
    :param device: Device address
    :param service: GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: DBus path
    """
    mngd_objs = get_managed_objects()

    _dbus_obj_path = None

    if adapter is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         '/org/bluez',
                                         constants.ADAPTER_INTERFACE,
                                         'Address',
                                         adapter)

    if device is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.DEVICE_INTERFACE,
                                         'Address',
                                         device)

    if service is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_SERVICE_IFACE,
                                         'UUID',
                                         service)

    if characteristic is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_CHRC_IFACE,
                                         'UUID',
                                         characteristic)

    if descriptor is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_DESC_IFACE,
                                         'UUID',
                                         descriptor)
    return _dbus_obj_path


class BluezDBusClient:

    def __init__(self):
        self.con = Gio.DBusObjectManagerClient.new_for_bus_sync(
            bus_type=Gio.BusType.SYSTEM,
            flags=Gio.DBusObjectManagerClientFlags.NONE,
            name='org.bluez',
            object_path='/',
            get_proxy_type_func=None,
            get_proxy_type_user_data=None,
            cancellable=None,
        )
        self.con.connect('object-added', self._on_object_added)
        self.con.connect('object-removed', self._on_object_removed)
        self.con.connect('interface-proxy-properties-changed',
                         self._on_properties_changed)
        self.on_object_added = None
        self.on_object_removed = None
        self.on_properties_changed = None

    def get_proxy(self, dbus_object, iface):
        method_proxy = self.con.get_interface(dbus_object, iface)
        prop_proxy = self.con.get_interface(dbus_object, 'org.freedesktop.Properties')
        return method_proxy

    def _on_object_added(self,
                         dbus_obj_mngr: Gio.DBusObjectManager,
                         dbus_object: Gio.DBusObject) -> None:
        ifaces = [iface.get_interface_name() for iface in dbus_object.get_interfaces()]
        dbus_path = dbus_object.get_object_path()
        for iface in ifaces:
            if iface.startswith('org.bluez'):
                logger.debug('object added on interface %s', iface)
                dev_props = get_managed_objects().get(dbus_path, {})
                if self.on_object_added:
                    self.on_object_added(dbus_path, dev_props)

    def _on_object_removed(self,
                           dbus_obj_mngr: Gio.DBusObjectManager,
                           dbus_object: Gio.DBusObject) -> None:

        ifaces = [iface.get_interface_name() for iface in dbus_object.get_interfaces()]
        dbus_path = dbus_object.get_object_path()

        if self.on_object_removed:
            for iface in ifaces:
                if iface.startswith('org.bluez'):
                    self.on_object_removed(dbus_path)

    def _on_properties_changed(
            self,
            dbus_client: Gio.DBusObjectManagerClient,
            object_proxy: Gio.DBusObjectProxy,
            interface_proxy: Gio.DBusProxy,
            changed_properties: GLib.Variant,
            invalidated_properties: list):
        # print('Properites changed')
        # print('\t', dbus_client)
        # print('\t', object_proxy.get_object_path())
        # print('\t', interface_proxy.get_interface_name())
        # print('\t', changed_properties.unpack())
        # print('\t', invalidated_properties)
        # dbus_proxy = Gio.DBusProxy.new_for_bus_sync(
        #     bus_type=Gio.BusType.SYSTEM,
        #     flags=Gio.DBusProxyFlags.NONE,
        #     info=None,
        #     name='org.bluez',
        #     object_path=object_proxy.get_object_path(),
        #     interface_name=interface_proxy.get_interface_name(),
        #     cancellable=None
        # )
        if self.on_properties_changed:
            # dbus_proxy = BluezDBusObject(object_proxy.get_object_path(),
            #                              interface_proxy.get_interface_name())
            self.on_properties_changed(object_proxy.get_object_path(),
                                       interface_proxy.get_interface_name(),
                                       changed_properties.unpack(),
                                       invalidated_properties)


class DbusService:

    def __init__(self, introspection_xml, publish_path):
        self.node_info = Gio.DBusNodeInfo.new_for_xml(introspection_xml).interfaces[0]
        # start experiment
        method_outargs = {}
        method_inargs = {}
        property_sig = {}
        for method in self.node_info.methods:
            method_outargs[method.name] = '(' + ''.join([arg.signature for arg in method.out_args]) + ')'
            method_inargs[method.name] = tuple(arg.signature for arg in method.in_args)
        self.method_inargs = method_inargs
        self.method_outargs = method_outargs
        # End experiment
        self.con = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        self.con.register_object(
            publish_path,
            self.node_info,
            self.handle_method_call,
            self.prop_getter,
            self.prop_setter)

    def handle_method_call(self,
                           connection: Gio.DBusConnection,
                           sender: str,
                           object_path: str,
                           interface_name: str,
                           method_name: str,
                           params: GLib.Variant,
                           invocation: Gio.DBusMethodInvocation
                           ):
        """
        This is the top-level function that handles method calls to
        the server.
        """
        # Start experiment
        args = list(params.unpack())
        for i, sig in enumerate(self.method_inargs[method_name]):
            if sig == 'h':
                msg = invocation.get_message()
                fd_list = msg.get_unix_fd_list()
                args[i] = fd_list.get(args[i])
        # End experiment
        func = self.__getattribute__(method_name)
        # result = func(*params)
        result = func(*args)
        if result is None:
            result = ()
        else:
            result = (result,)
        outargs = ''.join([_.signature
                           for _ in invocation.get_method_info().out_args])
        send_result = GLib.Variant(f'({outargs})', result)
        print(f'Send result {repr(send_result)}')
        invocation.return_value(send_result)

    def prop_getter(self,
                    connection: Gio.DBusConnection,
                    sender: str,
                    object: str,
                    iface: str,
                    name: str):
        print('prop_getter', connection, sender, object, iface, name)
        py_value = self.__getattribute__(name)
        signature = self.node_info.lookup_property(name).signature
        if 'v' in signature:
            dbus_value = _build_variant(iface, name, signature, py_value)
            return dbus_value
        if py_value:
            return GLib.Variant(signature, py_value)
        return None

    def prop_setter(self,
                    connection: Gio.DBusConnection,
                    sender: str,
                    object: str,
                    iface: str,
                    name: str,
                    value: GLib.Variant):
        print('prop_setter', connection, sender, object, iface, name, value)
        # x_value = GLib.Variant('as', ['test'])
        self.__setattr__(name, value.unpack())
        return True


def _from_dict(dict_value):
    s_data = GLib.VariantDict.new()
    for key, value in dict_value.items():
        gvalue = GLib.Variant('ay', value)
        s_data.insert_value(key, gvalue)
    return s_data.end()


def build_dict_variant(dict_value, value_type):
    s_data = GLib.VariantDict.new()
    for key, value in dict_value.items():
        gvalue = GLib.Variant(value_type, value)
        s_data.insert_value(key, gvalue)
    return s_data.end()


class DBusProperty:
    """
    This is to allow Python properties to be converted to GLib Variants
    when used on a service that is published.
    """
    def __init__(self, signature, init_value):
        self._prop_signature = signature
        self._value = GLib.Variant(self._prop_signature, init_value)

    def __get__(self, instance, owner=None):
        # Example get
        # props_proxy.Get('(ss)', ADAPTER, 'Powered')
        # print('get prop', instance, '-', owner)
        print('getter', self._value)
        return self._value.unpack()

    def __set__(self, instance, value):
        print('setter in:', self._prop_signature, value, type(value))
        if self._prop_signature == 'a{sv}':
            self._value = _from_dict(value)
        else:
            self._value = GLib.Variant(self._prop_signature, value)

        print('setter', type(self._value), self._value)


def get_device_address_from_dbus_path(path):
    """
    Function to get the address of a remote device from
    a given D-Bus path. Path must include device part
    (e.g. dev_XX_XX_XX_XX_XX_XX)
    """
    for path_elem in path.split('/'):
        if path_elem.startswith('dev_'):
            return path_elem.replace("dev_", '').replace("_", ":")
    return ''


def get_adapter_address_from_dbus_path(path):
    """Return the address of the adapter from the a DBus path"""
    result = re.match(r'/org/bluez/hci\d+', path)
    mngd_objs = get_managed_objects()
    return mngd_objs[result.group(0)][constants.ADAPTER_INTERFACE]['Address']


class DBusManager(GObject.GObject):
    __gsignals__ = {
        'adapter-added': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
        'adapter-removed': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
        'device-added': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
        'device-removed': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
    }

    def __new__(cls, *args, **kwargs):
        # We want to always get the same instance of the
        # Gio.DBusObjectManagerClient
        if not hasattr(cls, '_mngr'):
            cls._mngr = super().__new__(cls, *args, **kwargs)
        return cls._mngr

    def __init__(self):
        # try-except is workaround to stop __init__ being run if this
        # instances has already been initialised.
        try:
            self._client
        except AttributeError:
            super().__init__()
            logger.debug('Gio DBus Object Manager Client init')
            self._client = Gio.DBusObjectManagerClient.new_for_bus_sync(
                bus_type=Gio.BusType.SYSTEM,
                flags=Gio.DBusObjectManagerClientFlags.NONE,
                name='org.bluez',
                object_path='/',
                get_proxy_type_func=None,
                get_proxy_type_user_data=None,
                cancellable=None,
            )
            self._client.connect('object-added', self._on_object_added)
            self._client.connect('object-removed', self._on_object_removed)

    def _on_object_added(self,
                         _object_manager: Gio.DBusObjectManager,
                         dbus_object: Gio.DBusObject) -> None:
        device_proxy = dbus_object.get_interface('org.bluez.Device1')
        adapter_proxy = dbus_object.get_interface('org.bluez.Adapter1')
        if adapter_proxy:
            adapter_addr = adapter_proxy.get_cached_property('Address').unpack()
            logger.debug('Adapter added: %s', adapter_addr)
            self.emit('adapter-added', adapter_addr)
        elif device_proxy:
            device_addr = device_proxy.get_cached_property('Address').unpack()
            logger.debug('Device added: %s', device_addr)
            self.emit('device-added', device_addr)

    def _on_object_removed(self, _object_manager: Gio.DBusObjectManager, dbus_object: Gio.DBusObject) -> None:
        device_proxy = dbus_object.get_interface('org.bluez.Device1')
        adapter_proxy = dbus_object.get_interface('org.bluez.Adapter1')

        if adapter_proxy:
            object_path = adapter_proxy.get_object_path()
            logger.debug('Adapter removed from: %s', object_path)
            self.emit('adapter-removed', object_path)
        elif device_proxy:
            object_path = device_proxy.get_object_path()
            logger.debug('Device removed from: %s', object_path)
            self.emit('device-removed', object_path)

    def get_iface_proxy(self, dbus_object_path, dbus_iface):
        return self._client.get_object(dbus_object_path).get_interface(dbus_iface)

    def get_prop_proxy(self, dbus_object_path):
        return self.get_iface_proxy(dbus_object_path, constants.DBUS_PROP_IFACE)

    def get_adapters(self):
        dongles = {}
        for obj_proxy in self._client.get_objects():
            proxy = obj_proxy.get_interface(constants.ADAPTER_INTERFACE)

            if proxy:
                address = proxy.get_cached_property('Address').unpack()
                dongles[address] = proxy

        return dongles

    def get_adapter(self, address):
        return self.get_adapters().get(address)

    def get_devices(self, adapter_address=None):
        devices = {}
        if adapter_address:
            adapter_proxy = self.get_adapter(adapter_address)
            adapter_path = adapter_proxy.get_object_path()

        for obj_proxy in self._client.get_objects():
            proxy = obj_proxy.get_interface(constants.DEVICE_INTERFACE)

            if proxy:
                proxy_path = proxy.get_object_path()

                if adapter_address:
                    path_start = adapter_path
                else:
                    path_start = '/org/bluez/hci'
                if proxy_path.startswith(path_start):
                    address = proxy.get_cached_property('Address').unpack()
                    devices[address] = proxy

        return devices

    def get_device(self, adapter_address, devce_address):
        return self.get_devices(adapter_address).get(devce_address)


if __name__ == '__main__':
    from bluezero import adapter
    from bluezero import device
    from bluezero import microbit

    mngr = DBusManager()
    # print(mngr.get_adapters())
    # print(mngr.get_devices('FC:F8:AE:8F:0C:A4'))
    logger.setLevel(logging.DEBUG)
    # print('adapters:', adapter.Adapter.available())
    # test = adapter.Adapter('FC:F8:AE:8F:0C:A4')
    # test.on_device_found = print
    # print(test)
    # test.nearby_discovery(10)
    # for dev in mngr.get_devices():
    #     print(dev)
    # # dev = mngr.get_device('FC:F8:AE:8F:0C:A4', 'E1:4B:6C:22:56:F0')
    # dev1 = device.Device('FC:F8:AE:8F:0C:A4', 'E1:4B:6C:22:56:F0')
    # print(dev1)
    # dev2 = device.Device('FC:F8:AE:8F:0C:A4', 'E1:4B:6C:22:56:F0')
    # print(dev2)
    for ubit in microbit.Microbit.available():
        print(dir(ubit))
