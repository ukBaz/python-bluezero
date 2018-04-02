############
System Setup
############

Overview
--------

Bluezero relies on the dbus interface of BlueZ. This version of Bluezero is
tested wtih BlueZ version **5.43**.  As the BlueZ DBus API is undergoing
changes between versions it is best to aim for that version when working
with Bluezero.
BlueZ 5.43 was chosen as the version to align with as this is the default version
of BlueZ in Debian Stretch which was the latest/popular version at the time of
release. This means it is likely that the Linux version you have installed will
have the correct version.
To check the version use bluetoothctl and type version::

    $ bluetoothctl -v
    5.43


More instructions are available in the `Getting Started
<https://ukbaz.github.io/howto/ubit_workshop.html>`_
workshop using a Raspberry Pi and a BBC micro:bit


Using Bluezero for a Peripheral role or beacon
----------------------------------------------

The BlueZ DBus API functionality associated with Bluetooth advertising
requires the Bluetooth daemon to be run with the experimental flag.
Advertising is used for Beacons and Peripheral role.
Experimental mode can be switched on by default in the bluetooth.service file

Edit bluetooth.service file to add --experimental flag e.g::

    sudo sed -i '/^ExecStart.*bluetoothd\s*$/ s/$/ --experimental/' /lib/systemd/system/bluetooth.service


Restart bluetoothd in experimental mode
=======================================

You will need to either, reboot or run::

    sudo systemctl daemon-reload
    sudo service bluetooth restart

The bluetoothd should now be set to run with the experimental flag by default.

To check the bluetoothd is running with the experimental flag::

    service bluetooth status


Change DBus permissions for Bluezero
------------------------------------

An application that is in the role of a Peripheral will be registered on the System
DBus. This requires for some modification of permissions so Bluezero will be using
the bus name of ``ukBaz.bluezero``. An example dbus configuration file is provided
and will need to be copied to the correct location::

    sudo cp examples/ukBaz.bluezero.conf /etc/dbus-1/system.d/.


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
