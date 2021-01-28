========
Examples
========

An example can often speed things up when you are trying to get started with
a library so there are few below.
There is also a `Getting Started
<https://ukbaz.github.io/howto/ubit_workshop.html>`_
workshop using a Raspberry Pi and a BBC micro:bit if you are new to Bluetooth.

Adapter
-------

This example prints out the status of the Bluetooth device on your Linux
computer. It also checks to see if it is enabled (powered) before scanning for
nearby Bluetooth devices:

.. literalinclude:: ../examples/adapter_example.py
    :language: python


Central Role
------------
This example uses the micro:bit API that has been written in Bluezero to
interact with the micro:bit

.. literalinclude:: ../examples/microbit_poll.py
    :language: python


Scanner: Eddystone
------------------

This example scans for beacons in the Eddystone URL format.
It will report on `URL beacons` <https://github.com/google/eddystone/tree/master/eddystone-url>.

.. literalinclude:: ../examples/eddystone_scanner.py
    :language: python


Beacon: Eddystone URL
---------------------

This example broadcasts a given URL in a format for the `Physical Web
<https://google.github.io/physical-web/>`_:

.. literalinclude:: ../examples/eddystone_url_beacon.py
    :language: python


Peripheral Role
---------------

This example transmits a randomly generated value to represent the temperature
of the CPU over the single characteristic.
Values are only updated when notification are switched on.

.. literalinclude:: ../examples/cpu_temperature.py
    :language: python


Peripheral - Nordic UART Service
--------------------------------

This service simulates a basic UART connection over two lines, TXD and RXD.

It is based on a proprietary UART service specification by Nordic Semiconductors.
Data sent to and from this service can be viewed using the nRF UART apps from Nordic
Semiconductors for Android and iOS.

.. literalinclude:: ../examples/ble_uart.py
    :language: python


Control Media Player over Bluetooth
-----------------------------------

This script displays information about the current track being playered by
the connected media player

.. literalinclude:: ../examples/control_media_player.py
    :language: python
