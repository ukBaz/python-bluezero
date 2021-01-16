#!/usr/bin/env bash

# Ensure Python virtual environment is loaded
. venv/bin/activate

python3 dev_tools/check_tests_included.py
dev1=$?
coverage run -m unittest -v tests.test_tools
test1001=$?
coverage run --append -m unittest -v tests.test_async_tools
test1002=$?
coverage run --append -m unittest -v tests.test_dbus_tools
test1003=$?
coverage run --append -m unittest -v tests.test_adapter
test1004=$?
coverage run --append -m unittest -v tests.test_advertisement
test1005=$?
coverage run --append -m unittest -v tests.test_device
test1006=$?
coverage run --append -m unittest -v tests.test_gatt
test1007=$?
coverage run --append -m unittest -v tests.test_dbus_tools_mock
test1008=$?
coverage run --append -m unittest -v tests.test_broadcaster
test101=$?
coverage run --append -m unittest -v tests.test_central
test102=$?
coverage run --append -m unittest -v tests.test_observer
test103=$?
coverage run --append -m unittest -v tests.test_peripheral
test11=$?
coverage run --append -m unittest -v tests.test_eddystone
test12=$?
coverage run --append -m unittest -v tests.test_microbit
test13=$?
# Tests for code in examples
coverage run --append -m unittest -v tests.test_adapter_example
test_example1=$?
coverage run --append -m unittest -v tests.test_adapter_example_db_mock
test_example2=$?
coverage run --append -m unittest -v tests.test_beacon_db_mock
test_example3=$?
coverage run --append -m unittest -v tests.test_eddystone_scanner_example
test_example4=$?
coverage run --append -m unittest -v tests.test_microbit_poll_example
test_example5=$?
coverage run --append -m unittest -v tests.test_find_microbit_db_mock
test_example6=$?
coverage run --append -m unittest -v tests.test_microbit_uart_db_mock
test_example7=$?
coverage run --append -m unittest -v tests.test_peripheral_db_mock
test_example8=$?


pycodestyle -v bluezero
lint_bluezero=$?
pycodestyle -v examples
lint_examples=$?
# pycodestyle -v tests
# lint_tests=$?

coverage report
coverage html
echo file://`pwd`/htmlcov/index.html
# google-chrome `pwd`/htmlcov/index.html &
group100=$((test1001 + test1002 + test1003 + test1004 + test1005 + \
            test1006 + test1007 + test1008))
group10=$((test101 + test102 + test103))
group1=$((test11 + test12 + test13))
group_examples=$((test_example1 + test_example2 + test_example3 + test_example4 + \
                  test_example5 + test_example6 + test_example7 + test_example8))
group_lint=$((lint_bluezero + lint_examples))
group_dev=$((dev1))
if [ $((group1 + group10 + group100 + group_examples + group_lint + group_dev)) -ne 0 ]; then
   echo -e "\n\n###  A test has failed!!  ###\n"
else
    echo -e "\n\nSuccess!!!\n"
fi

