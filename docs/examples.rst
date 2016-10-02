========
Examples
========

Level 1
=======

Adapter
-------

This example prints out the status of the Bluetooth device on your Linux
computer. It also checks to see if it is enabled (powered) before scanning for
nearby Bluetooth devices:

.. literalinclude:: ../examples/adapter_example.py

Eddystone URL Beacon
--------------------

This example broadcasts a given URL in a format for the `Physical Web
<https://google.github.io/physical-web/>`_:

.. literalinclude:: ../examples/eddystone-url-beacon.py

Level 10
========

Micro:bit Buttons
-----------------

This example reads the status of the buttons on a `BBC micro:bit
<https://en.wikipedia.org/wiki/Micro_Bit/>`_ and indicates them on a `Ryanteck
Traffic Hat <https://ryanteck.uk/hats/1-traffichat-0635648607122.html/>`_. (To
run this replace xx:xx:xx:xx:xx:xx with the address of your micro:bit):

    ``python3 microbit_button.py xx:xx:xx:xx:xx:xx``

.. literalinclude:: ../examples/level10/microbit_button.py

TI CC2650
---------

This example reads the sensors or buttons on a `TI SensorTag
<http://www.ti.com/tool/TIDC-CC2650STK-SENSORTAG/>`_ and prints them out to the
screen:

.. literalinclude:: ../examples/level10/read_sensortag_CC2650.py

Level 100
=========

Physical Web FatBeacon
----------------------

This example advertises a Physical Web Beacon using the Eddystone standard.
Currently this can only be connected to by the Physical Web app because that is
the only thing that supports `FatBeacons
<https://github.com/google/physical-web/issues/784>`_:

.. literalinclude:: ../examples/level100/fatbeacon.py
