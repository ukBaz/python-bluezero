#!/usr/bin/env bash
python -m unittest -v tests.test_url_to_hex
test1=$?
python3 -m unittest -v tests.test_url_to_hex
test2=$?
python -m unittest -v tests.test_adapter
test3=$?
python3 -m unittest -v tests.test_adapter
test4=$?
python -m unittest -v tests.test_device
test5=$?
python3 -m unittest -v tests.test_device
test6=$?
pycodestyle -v bluezero
test7=$?
pycodestyle -v examples
test8=$?
pycodestyle -v tests
test9=$?

if [ $((test1 + test2 + test3 + test4 + test5 + test6 + test7 + test8 + test9)) -ne 0 ]; then
   echo -e "\n\n###  A test has failed!!  ###\n"
else
    echo -e "\n\nSuccess!!!\n"
fi
