#!/usr/bin/env bash
set -ex

wget https://github.com/ukBaz/python-dbusmock/archive/bluez_gatt.tar.gz -O /tmp/dbusmock.tar.gz
cd /tmp
tar -xvf dbusmock.tar.gz
