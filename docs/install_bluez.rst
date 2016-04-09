*****
Packages that need available
*****
The following packages is a super set of what is required. For some systems these may already be install or not required.
.. code-block::
    sudo apt-get install bluetooth
    sudo apt-get install bluez-tools
    # Not required if building from source
    # sudo apt-get install bluez-test-scripts
    # sudo apt-get install bluez-hcidump
    # sudo apt-get install python-bluez

To compile a new version of Bluez:
.. code-block::
    sudo apt-get install build-essential
    sudo apt-get install autoconf
    sudo apt-get install glib2.0
    sudo apt-get install libglib2.0-dev
    sudo apt-get install libdbus-1-dev
    sudo apt-get install libudev-dev
    sudo apt-get install libical-dev
    sudo apt-get install libreadline-dev

If you are looking to development of Bluezero then you will need:
.. code-block::
    sudo apt-get install rsync
    sudo apt-get install python-dbus
    sudo apt-get install python3-dbus
    sudo apt-get install python-dbusmock
    # Do I need the following?
    sudo apt-get install python3-dbusmock



Getting newer versions of Bluez
****

Download the User Space BlueZ Package from:
http://www.bluez.org/download/

.. code-block::
    wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.39.tar.xz
    tar xf bluez-5.39.tar.xz
    cd bluez-5.39

How to compile Bluez 5.36 and later
To configure run:
.. code-block::
    ./configure --prefix=/usr \
                --mandir=/usr/share/man \
                --sysconfdir=/etc \
                --localstatedir=/var \
                --enable-experimental \
                --enable-maintainer-mode

To compile and install run:
.. code-block::
    make && sudo make install



Automatically run bluetoothd with experimental mode
****
Edit bluetooth.service file. e.g.
.. code-block::
sudo vi /lib/systemd/system/bluetooth.service

Before:
    ExecStart=/usr/libexec/bluetooth/bluetoothd
After:
    ExecStart=/usr/libexec/bluetooth/bluetoothd -E


Previously it has been required to add the setting of ‘ControllerMode = le’ to the /etc/bluetooth/main.conf and when
the Linux advertises it now has the 'BR/EDR Not supported' flag set.

Debug options
****
Monitor the bluetooth hci traffic
.. code-block::
    sudo btmon -t |& tee ~/btmon.log

Log the bluetoothd
Stop bluetooth service:
.. code-block::
    service bluetooth stop

Kill the process (use ‘service bluetooth status’ to get the pid) the launch daemon with debug:
.. code-block::
    sudo /usr/libexec/bluetooth/bluetoothd -nEd |& tee ~/bluetoothd.log

Monitor dbus traffic
.. code-block::
    dbus-monitor --system

Manually run bluetoothd with experimental mode with debug:
.. code-block::
    /usr/libexec/bluetooth/bluetoothd -nEd

