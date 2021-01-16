"""Global constants file for the python-bluezero project.

This file is a single location for the different object paths that are used as
constants around the python-bluezero library.

:Example:

.. code-block:: python

   from bluezero import constants
   my_function(constants.CONST_1, constants.CONST_2)

"""

# General D-Bus Object Paths
#: The DBus Object Manager interface
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
#: DBus Properties interface
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

# General Bluez D-Bus Object Paths
#: BlueZ DBus Service Name
BLUEZ_SERVICE_NAME = 'org.bluez'
#: BlueZ DBus adapter interface
ADAPTER_INTERFACE = 'org.bluez.Adapter1'
#: BlueZ DBus device Interface
DEVICE_INTERFACE = 'org.bluez.Device1'

# Bluez GATT D-Bus Object Paths
#: BlueZ DBus GATT manager Interface
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
#: BlueZ DBus GATT Profile Interface
GATT_PROFILE_IFACE = 'org.bluez.GattProfile1'
#: BlueZ DBus GATT Service Interface
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
#: BlueZ DBus GATT Characteristic Interface
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
#: BlueZ DBus GATT Descriptor Interface
GATT_DESC_IFACE = 'org.bluez.GattDescriptor1'

# Bluez Advertisment D-Bus object paths
#: BlueZ DBus Advertising Manager Interface
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
#: BlueZ DBus Advertisement Interface
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'

# Bluez Media D-Bus object paths
#: BlueZ DBus Media player Interface
MEDIA_PLAYER_IFACE = 'org.bluez.MediaPlayer1'

# Bluezero local D-Bus publish location
#: Bluezero D-Bus Name
BLUEZERO_DBUS_NAME = 'ukBaz.bluezero'
#: Bluezero D-Bus object root
BLUEZERO_DBUS_OBJECT = '/ukBaz/bluezero'
