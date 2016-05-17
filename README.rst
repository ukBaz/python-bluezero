===============
python-bluezero
===============
.. image:: https://travis-ci.org/ukBaz/python-bluezero.svg
    :target: https://travis-ci.org/ukBaz/python-bluezero
    :alt: Build Status

A simple Python interface to Bluez stack

Name and aim
============
The aim of this library is to provide an API to access to _Bluez_ with _zero_ boilerplate code.

Goal
====
To provide a simplified API to people that want to use Bluetooth functionality in their code.
The library will use calls to the Bluez D-Bus API and use 'sensible' defaults to help with that simplification.
It aims to support the ability to create interesting STEM activities without needing to 
explain the Bluez API or write an event loop.

In addition to the API it will contain examples of how to connect to common Bluetooth Smart (BLE) objects 
around them (or at least easily accessible to them).
These examples will need to be written without the need to sign (or break) non-disclosure agreements.

Status
======
This is an early-stage experiment that we are developing in the open.
This *currently* should only be of interest to developers looking to provide feedback and to contribute.

Examples
========
If you are coming here for the first time then looking at the examples is probably the place to start

GATT Server (Peripheral role)
-----------------------------
light_switch.py - Experiment to split user code from library code


The rest of the experiments are just big code blobs that were just to prove we can do the required things.
Not guaranteed to work beyond the specific hardware of the developers
Beacon
------
eddystone-url-beacon.py - Simple Eddystone URL beacon. Enter URL get beacon out

Scanner
-------
No example currently. see issue [#11] (https://github.com/ukBaz/python-bluezero/issues/11)

GATT Server (Peripheral role)
-----------------------------
battery_service.py - Based heavily on the Bluez examples and reports fake heart rate and battery levels

GATT Client (Central role)
--------------------------
read_sensortag_CC2650.py - This is a simple example of how to read the Ti Sensortag CC2650
