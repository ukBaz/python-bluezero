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

Central Device
--------------
This example uses the micro:bit API that has been written in bluezero to interact
with the micro:bit

.. literalinclude:: ../examples/microbit_poll.py


Eddystone URL Beacon
--------------------

This example broadcasts a given URL in a format for the `Physical Web
<https://google.github.io/physical-web/>`_:
You will need to put the BlueZ bluetoothd into experimental mode for this one.

.. literalinclude:: ../examples/eddystone-url-beacon.py


cpu_temperature.py
------------------

This example transmits the temperature of the CPU over the single characteristic.
If your hardware does not support the `vcgencmd` then change the `get_cpu_temperature()`
function to use the randomly generated temperature.
Values are only updated when notification are switched on.
You will need to have BlueZ in experimental mode and have tweaked the DBus configuration
file to open the permissions for 'ukBaz.bluezero'

.. literalinclude:: ../examples/cpu_temperature.py


Eddystone Scanner
--------------------

This example scans for beacons in the Eddystone format.
It will report on `UID beacons` <https://github.com/google/eddystone/tree/master/eddystone-uid>
and `URL beacons` <https://github.com/google/eddystone/tree/master/eddystone-url>.

This uses the `aioblescan` Python library which requires your code to be run with `sudo`

.. literalinclude:: ../examples/eddystone-scanner.py
