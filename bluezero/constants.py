"""Global constants file for the python-bluezero project.

This file is a single location for the different object paths that are used as
constants around the python-bluezero library.

:Example:

.. code-block:: python

   from bluezero import constants
   my_function(constants.CONST_1, constants.CONST_2)

"""

# General D-Bus Object Paths
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

# General Bluez D-Bus Object Paths
BLUEZ_SERVICE_NAME = 'org.bluez'
ADAPTER_INTERFACE = 'org.bluez.Adapter1'
DEVICE_INTERFACE = 'org.bluez.Device1'

# Bluez GATT D-Bus Object Paths
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE = 'org.bluez.GattDescriptor1'

# Bluez Advertisment D-Bus object paths
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
