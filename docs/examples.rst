========
Examples
========

An example can often speed things up when you are trying to get started with
a library so there are few below.
There is also a `Getting Started
<https://ukbaz.github.io/howto/ubit_workshop.html>`_
workshop using a Raspberry Pi and a BBC micro:bit

Adapter
-------

This example prints out the status of the Bluetooth device on your Linux
computer. It also checks to see if it is enabled (powered) before scanning for
nearby Bluetooth devices:

.. literalinclude:: ../examples/adapter_example.py

Central Role
------------
This example uses the micro:bit API that has been written in Bluezero to interact
with the micro:bit

.. literalinclude:: ../examples/microbit_poll.py


Scanner: Eddystone
------------------

This example scans for beacons in the Eddystone format.
It will report on `UID beacons` <https://github.com/google/eddystone/tree/master/eddystone-uid>
and `URL beacons` <https://github.com/google/eddystone/tree/master/eddystone-url>.

This uses the `aioblescan` Python library which requires your code to be run with `sudo`

.. literalinclude:: ../examples/eddystone-scanner.py

Beacon: Eddystone URL
---------------------

This example broadcasts a given URL in a format for the `Physical Web
<https://google.github.io/physical-web/>`_:
You will need to put the BlueZ bluetoothd into experimental mode for this one.

.. literalinclude:: ../examples/eddystone-url-beacon.py


Peripheral Role
---------------

This example transmits the temperature of the CPU over the single characteristic.
If your hardware does not support the `vcgencmd` then change the `get_cpu_temperature()`
function to use the randomly generated temperature.
Values are only updated when notification are switched on.
You will need to have BlueZ in experimental mode and have modified the DBus configuration
file to open the permissions for 'ukBaz.bluezero'

.. literalinclude:: ../examples/cpu_temperature.py


Peripheral - Nordic UART Service
--------------------------------

This service simulates a basic UART connection over two lines, TXD and RXD.

It is based on a proprietary UART service specification by Nordic Semiconductors.
Data sent to and from this service can be viewed using the nRF UART apps from Nordic
Semiconductors for Android and iOS.

It uses the Bluezero peripheral file (level 10) so should be easier than the previous CPU
Temperature example that was a level 100.

.. literalinclude:: ../examples/ble_uart.py


Control Media Player over Bluetooth
-----------------------------------

This script displays information about the current track being playered by
the connected media player

.. literalinclude:: ../examples/control_media_player.py