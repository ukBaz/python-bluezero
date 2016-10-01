.. image:: asset/bluez_logo.jpg

********
Overview
********

Bluetooth
=========

Bluetooth is a standard set of binary protocols for short-range wireless
communication between devices.

* Bluetooth "Classic" (BR/EDR) supports speeds up to about 24Mbps.
* Bluetooth 4.0 introduces a low energy mode, *"Bluetooth Low Energy"*
  (BLE or LE, also known as *"Bluetooth Smart"*), that operates at 1Mbps.
  This mode allows devices to leave their transmitters off most of the time.
  As a result it is "Low Energy".

BLE functionality is dominated by key/value pairs that create a
*Generic Attribute Profile* (GATT).

BLE defines multiple roles that devices can play:

* The *Broadcaster* (beacon) is a transmitter only application.
* The *Observer* (scanner) is for receiver only applications.
* Devices acting in the *Peripheral* role can receive connections.
* Devices acting in the *Central* role can connect to Peripheral devices.

BlueZ
=====

BlueZ is a Bluetooth stack for the Linux family of operating systems. Support
for BlueZ can be found in many Linux distributions available.

The highest level of API on BlueZ is the DBus API which can be daunting to
users unfamiliar with such APIs. ``python-bluezero`` offers users a more gentle
learning curve to using Bluetooth functionality on Linux.

Bluezero API Complexity
=======================

This section gives guidelines about the complexity of different
``python-bluezero`` APIs. We will use the terms Level 1, 10 and 100. A new user
would start at Level 1 as this should offer the least friction. If at a later
stage a greater level of control is needed then the user can progress on to the
other levels. As the user becomes more experienced they may not need Bluezero
and will use BlueZ on its own. The numbers for the API levels represent the
steps in code and knowledge required with each step.

Level 1
-------
- At this level the interface will be pythonic.
- No knowledge of Bluetooth, DBus and event loops will be assumed.
- For something to exist at this level there will need to be a public
  Bluetooth Profile in existence so that users don’t need to enter UUIDs etc.
- This might be specific hardware such as the BBC *micro:bit* or it could be
  more generalised hardware such as Heart Rate Monitors.

Level 10
--------
- At this level the interface is still pythonic.
- Some knowledge of Bluetooth such as UUIDs, services and characteristics
  will be assumed.
- It will not make reference to DBus or event loops.

Level 100
---------
- At this level the interface is expecting the user to know Bluetooth, DBus
  and event loops.
- DBus function names are not Pythonic but will be exposed at the level.
- This level will be very specific to the Linux kernel and so it will be
  difficult to port this to other operating systems that do not have the
  Bluez Daemon running.
- The previous more abstracted API levels should be easier to port to any
  hardware.


Summary of Bluezero Files
-------------------------

+------------------+----------------+--------------+--------------+
|  Level 1         | Level 10       | Level 100    |    shared    |
+==================+================+==============+==============+
| automation_io.py | broadcaster.py | adapter.py   | tools.py     |
+------------------+----------------+--------------+--------------+
| eddystone-URL.py | central.py     | advertise.py | constants.py |
+------------------+----------------+--------------+--------------+
| microbit.py      | observer.py    | device.py    |              |
+------------------+----------------+--------------+--------------+
|                  | peripheral.py  | GATT.py      |              |
+------------------+----------------+--------------+--------------+
|                  | scanner.py     | localGATT.py |              |
+------------------+----------------+--------------+--------------+
