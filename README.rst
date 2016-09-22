===============
python-bluezero
===============
.. image:: https://travis-ci.org/ukBaz/python-bluezero.svg
    :target: https://travis-ci.org/ukBaz/python-bluezero
    :alt: Build Status

.. image:: https://codeclimate.com/github/ukBaz/python-bluezero/badges/gpa.svg
   :target: https://codeclimate.com/github/ukBaz/python-bluezero
   :alt: Code Climate
   
.. image:: https://codeclimate.com/github/ukBaz/python-bluezero/badges/coverage.svg
   :target: https://codeclimate.com/github/ukBaz/python-bluezero/coverage
   :alt: Test Coverage

.. image:: https://codeclimate.com/github/ukBaz/python-bluezero/badges/issue_count.svg
   :target: https://codeclimate.com/github/ukBaz/python-bluezero
   :alt: Issue Count


A simple Python interface to Bluez stack

Name and aim
============
The aim of this library is to provide an API to access to *Bluez* with *zero* boilerplate code.

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

Adapter
-------
adapter_example.py
******************
This will check that it can find the Bluetooth adapter on the computer running the code.
It will print to screen various information and check it is powered before scanning for
nearby devices

GATT Client (Central role)
--------------------------
read_sensortag_CC2650.py
************************
This is a simple example of how to read the Ti Sensortag CC2650
microbit_button.py
******************
This example

Beacon
------
eddystone-url-beacon.py
***********************
Simple Eddystone URL beacon. Can be read with any Physical Web application
fatbeacon.py
************
Experiment with Eddystone FatBeacon. Contains service for beacon to connect to that sends html page.

Scanner
-------
No example currently.

GATT Server (Peripheral role)
-----------------------------
No working example