############
System Setup
############

Overview
--------

Bluezero relies on the dbus interface of BlueZ. This version of Bluezero is
tested wtih BlueZ version **5.50**.  As the BlueZ DBus API is undergoing
changes between versions it is best to aim for that version when working
with Bluezero.
BlueZ 5.50 was chosen as the version to align with as this is the default version
of BlueZ in Debian Stretch which was the latest/popular version at the time of
release. This means it is likely that the Linux version you have installed will
have the correct version.
To check the version use bluetoothctl and type version::

    $ bluetoothctl -v
    5.50


More instructions are available in the `Getting Started
<https://ukbaz.github.io/howto/ubit_workshop.html>`_
workshop using a Raspberry Pi and a BBC micro:bit

Notes for getting debug information
-----------------------------------

Monitor the bluetooth hci traffic
=================================

Use Bluetooth monitor tool::

    sudo btmon -w ~/btmon.log

Log of the bluetoothd
=====================
Stop bluetooth service::

    service bluetooth stop

Kill the process (use ‘service bluetooth status’ to get the pid) the launch
daemon with debug::

    sudo /usr/libexec/bluetooth/bluetoothd -nEd |& tee ~/bluetoothd.log

Manually run bluetoothd with experimental mode with debug::

    /usr/libexec/bluetooth/bluetoothd -nEd

Monitor dbus traffic
====================
debug probe to print message bus messages::

    dbus-monitor --system
