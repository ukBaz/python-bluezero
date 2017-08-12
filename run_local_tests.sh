#!/usr/bin/env bash
coverage run -m unittest -v tests.test_tools
test1001=$?
# python -m unittest -v tests.test_adapter
# test21=$?
coverage run --append -m unittest -v tests.test_adapter
test1002=$?
coverage run --append -m unittest -v tests.test_device
test1003=$?
coverage run --append -m unittest -v tests.test_gatt
test1004=$?
coverage run --append -m unittest -v tests.test_broadcaster
test101=$?
coverage run --append -m unittest -v tests.test_peripheral
test102=$?
coverage run --append -m unittest -v tests.test_blinkt
test11=$?
coverage run --append -m unittest -v tests.test_eddystone
test12=$?
coverage run --append -m unittest -v tests.test_microbit
test13=$?
coverage run --append -m unittest -v tests.test_adapter_example
test_example1=$?
pycodestyle -v bluezero
lint_bluezero=$?
pycodestyle -v examples
lint_examples=$?
# pycodestyle -v tests
# test53=$?

coverage report
group100=$((test1001 + test1002 + test1003 + test1004))
group10=$((test101 + test102))
group1=$((test11 + test12 + test13))
group_exampels=$((test_example1))
group_lint=$((lint_bluezero + lint_examples))
if [ $((group1 + group10 + group100 + group_examples + group_lint)) -ne 0 ]; then
   echo -e "\n\n###  A test has failed!!  ###\n"
else
    echo -e "\n\nSuccess!!!\n"
fi

