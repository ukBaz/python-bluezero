# python-bluezero  [![Build Status](https://travis-ci.org/ukBaz/python-bluezero.svg)](https://travis-ci.org/ukBaz/python-bluezero)
A simple Python interface to Bluez stack

## Name and aim
The aim of this library is to provide an API to access to _Bluez_ with _zero_ boilerplate code.

## Goal
To provide a simplified API to people that want to use Bluetooth functionality in their code.
The library will use calls to the Bluez D-Bus API and use 'sensible' defaults to help with that simplification.
It aims to support the ability to create interesting STEM activities without needing to 
explain the Bluez API or write an event loop.

In addition to the API it will contain examples of how to connect to common Bluetooth Smart (BLE) object 
around them (or at least easily accessible to them easily).
This will need to be done without the need to sign (or break) non-disclosure agreements.
