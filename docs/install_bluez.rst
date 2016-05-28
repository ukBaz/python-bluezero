################
Installing Bluez
################

Overview
--------
Bluezero relies on the dbus interface of Bluez. This is still under an 'experimental' flag and is changing rapidly whuch currently means that it is unlikely that the Linux version you have installed with have the correct version or the experimental flag set.
This instructions are intended to jump start the switching to a newer version of Bluez which will need to be built from source.

Packages that need available
----------------------------
The following packages is a super set of what is required. For some systems these may already be
install or not required::
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

If you are looking to development of Bluezero then you will need::

    sudo apt-get install rsync
    sudo apt-get install python-dbus
    sudo apt-get install python3-dbus
    sudo apt-get install python-dbusmock
    # Do I need the following?
    sudo apt-get install python3-dbusmock



Getting newer versions of Bluez source
--------------------------------------

Download the User Space BlueZ Package from http://www.bluez.org/download/ ::

    wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.40.tar.xz
    tar xf bluez-5.40.tar.xz
    cd bluez-5.40

How to config and compile Bluez 5.36 and later
----------------------------------------------
To configure run::

    ./configure --prefix=/usr \
                --mandir=/usr/share/man \
                --sysconfdir=/etc \
                --localstatedir=/var \
                --enable-experimental \
                --enable-maintainer-mode

To compile and install run::

    make && sudo make install

Automatically run bluetoothd with experimental mode
---------------------------------------------------
Edit bluetooth.service file to add --experimental flag e.g::

    sudo sed -i '/^ExecStart.*bluetoothd\s*$/ s/$/ --experimental/' /lib/systemd/system/bluetooth.service

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

Kill the process (use ‘service bluetooth status’ to get the pid) the launch daemon with debug::

    sudo /usr/libexec/bluetooth/bluetoothd -nEd |& tee ~/bluetoothd.log

Manually run bluetoothd with experimental mode with debug::

    /usr/libexec/bluetooth/bluetoothd -nEd

Monitor dbus traffic
====================
debug probe to print message bus messages::

    dbus-monitor --system

