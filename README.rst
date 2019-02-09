===============
python-bluezero
===============
.. image:: https://travis-ci.org/ukBaz/python-bluezero.svg
    :target: https://travis-ci.org/ukBaz/python-bluezero
    :alt: Build Status

.. image:: https://img.shields.io/codecov/c/github/ukBaz/python-bluezero/master.svg?maxAge=2592000
    :target: https://codecov.io/github/ukBaz/python-bluezero
    :alt: Code Coverage

.. image:: https://img.shields.io/pypi/v/bluezero.svg
   :target: https://pypi.python.org/pypi/bluezero/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/l/bluezero.svg
   :target: https://github.com/ukBaz/python-bluezero/blob/master/LICENSE
   :alt: MIT License



A simple Python interface to BlueZ stack

Name and aim
============
The aim of this library is to provide an API to access to *Bluez* with *zero* boilerplate code.

Goal
====
To provide a simplified API to people that want to use Bluetooth functionality in their code.
The library will use calls to the BlueZ D-Bus API and use 'sensible' defaults to help with that simplification.
It aims to support the ability to create interesting STEM activities without needing to 
explain the BlueZ API or write an event loop.

In addition to the API it will contain examples of how to connect to common Bluetooth Smart (BLE) objects 
around them (or at least easily accessible to them).
These examples will need to be written without the need to sign (or break) non-disclosure agreements.

Status
======
While we want this to be easy to use it does not mean it easy to create.
This library is still in the early stages so things might change and break. Apologies in advance!
We will try to make it as stable as possible. However much of the functionality that is in BlueZ is
still flagged as experimental.
The library assumes you are using a Linux release with BlueZ 5.43. For example Raspbian Stretch


Getting Started
===============
If you are here for the time, and especially if you are new to Bluetooth Low Energy, then
a tutorial might be a good place to start.
The following tutorial has been created based on the readily available hardware of
a Raspberry Pi 3 and a micro:bit. More details available at:
https://ukbaz.github.io/howto/ubit_workshop.html

Examples
========
There are some other examples in the library if you are feeling adventurous

Adapter
-------

adapter_example.py
******************
This will check that it can find the Bluetooth adapter on the computer running the code.
It will print to screen various information and check it is powered before scanning for
nearby devices

GATT Client (Central role)
--------------------------

microbit_poll.py
****************
This example uses the micro:bit API that has been written in bluezero.
You will need a buzzer attached to pin 0 to get play_beep to work.

Beacon
------

eddystone-url-beacon.py
***********************
You will need to put the BlueZ bluetoothd into experimental mode for this one.
More details elsewhere in the documentation.
A Simple Eddystone URL beacon.
You can be read the URL being broadcast with any Physical Web application on your Phone

Scanner
-------

eddystone-scanner.py
********************

This example scans for beacons using the Eddystone format.
It will report on `UID beacons` and `URL beacons`.

This uses the `aioblescan` Python library which requires your code to be run with `sudo`.

GATT Server (Peripheral role)
-----------------------------
This is starting to be very experimental...
You will need to have BlueZ in experimental mode and have tweaked the dbus configuration
file to open the permissions for 'ukBaz.bluezero'

cpu_temperature.py
******************

This example transmits the temperature of the CPU over the single characteristic.
If your hardware does not support the `vcgencmd` then change the `get_cpu_temperature()`
function to use the randomly generated temperature.
Values are only updated when notification are switched on.

ble_uart.py
-----------

This example simulates a basic UART connection over two lines, TXD and RXD.

It is based on a proprietary UART service specification by Nordic Semiconductors.
Data sent to and from this service can be viewed using the nRF UART apps from Nordic
Semiconductors for Android and iOS.

It uses the Bluezero peripheral file (level 10) so should be easier than the previous CPU
Temperature example that was a level 100.