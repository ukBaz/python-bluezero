################
Installing Bluez
################

Overview
--------

Bluezero relies on the dbus interface of Bluez.  This library requires the
features provided by Bluez version **5.43** and later.  As this is as recent
build,  it is unlikely that the Linux version you have installed will have the
correct version. These instructions are intended to jump start the switching to
a newer version of Bluez which will need to be built from source.

Packages that need available
----------------------------

The following packages are a super set of what is required. For some systems
these may already be install or not required::

    sudo apt-get install bluetooth
    sudo apt-get install bluez-tools
    # Not required if building from source
    # sudo apt-get install bluez-test-scripts
    # sudo apt-get install bluez-hcidump
    # sudo apt-get install python-bluez

To compile a new version of Bluez::

    sudo apt-get install build-essential
    sudo apt-get install autoconf
    sudo apt-get install glib2.0
    sudo apt-get install libglib2.0-dev
    sudo apt-get install libdbus-1-dev
    sudo apt-get install libudev-dev
    sudo apt-get install libical-dev
    sudo apt-get install libreadline-dev

If you are looking to contribute to the development of Bluezero then you will
need::

    sudo apt-get install rsync
    sudo apt-get install python-dbus
    sudo apt-get install python3-dbus
    sudo apt-get install python-dbusmock
    # Do I need the following?
    sudo apt-get install python3-dbusmock

There are also some pip installs required for development::

    # For doing Sphinx documentation
    sudo pip3 install Sphinx
    sudo pip3 install sphinx_rtd_theme
    # To check code against PEP 8 style conventions
    sudo pip3 install pycodestyle

Getting newer versions of Bluez source
--------------------------------------

Download the User Space BlueZ Package from http://www.bluez.org/download/ ::

    wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.43.tar.xz
    tar xf bluez-5.43.tar.xz
    cd bluez-5.43

How to config and compile Bluez 5.43 and later
----------------------------------------------
To configure run::

    ./configure --prefix=/usr \
                --mandir=/usr/share/man \
                --sysconfdir=/etc \
                --localstatedir=/var \
                --enable-experimental \
                --enable-maintainer-mode

.. note::
    On the Raspberry Pi 3 installing the latest version of BlueZ breaks the connection
    to the controller. See Bluezero GitHub repository `issue 30
    <https://github.com/ukBaz/python-bluezero/issues/30#issuecomment-250594754>`_
    on how to patch BlueZ to use with a Raspberry Pi 3

To compile and install run::

    make -j 4 && sudo make install

Automatically run bluetoothd with experimental mode
---------------------------------------------------
Some of the BlueZ DBus API functionality is still behind an experimental flag.
This can be switch on by default in the bluetooth.service file

Edit bluetooth.service file to add --experimental flag e.g::

    sudo sed -i '/^ExecStart.*bluetoothd\s*$/ s/$/ --experimental/' /lib/systemd/system/bluetooth.service

Restart bluetoothd with new version
-----------------------------------
You will need to either, reboot or run::

    sudo systemctl daemon-reload
    sudo service bluetooth restart

The bluetoothd should now be the new version. To check the bluetoothd is
running::

    service bluetooth status

To check the version use bluetoothctl and type version::

    $ bluetoothctl
    [bluetooth]# version
    Version 5.43

Switch controller to Bluetooth Low Energy only
----------------------------------------------

Much of what Bluezero is doing is using Bluetooth Low Energy. It has been
discovered to get reliable connection to Android phones it is best to put the
controller into le only mode. This is done in the ``/etc/bluetooth/main.conf``
file. Ensure that it contains the following::

    ControllerMode = le

Creating a Bluezero peripheral
------------------------------

A peripheral application will be registered on the DBus using the bus name of
``ukBaz.bluezero``. An example dbus configuration file is provided and will
need to be copied to the correct location::

    sudo cp examples/ukBaz.bluezero.conf /etc/dbus-1/system.d/.


Notes for getting debug information
-----------------------------------
Monitor the bluetooth hci traffic
=================================
Use Bluetooth monitor tool::

    sudo btmon -t |& tee ~/btmon.log

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
