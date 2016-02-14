#!/bin/bash
case "${TRAVIS_PYTHON_VERSION}" in
    2.7)
        # Sort out loading of python modules
        sudo apt-get install -qq python-gi
        sudo apt-get install -qq python-dbus
        ;;
    3.3)
        # load python 3 modules
        sudo apt-get install -qq python3-gi
        sudo apt-get install -qq python3-dbus
        ;;
esac