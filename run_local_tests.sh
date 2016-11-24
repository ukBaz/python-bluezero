#!/usr/bin/env bash
python -m unittest -v tests.test_tools
test11=$?
python3 -m unittest -v tests.test_tools
test12=$?
python -m unittest -v tests.test_adapter
test21=$?
python3 -m unittest -v tests.test_adapter
test22=$?
python -m unittest -v tests.test_device
test31=$?
python3 -m unittest -v tests.test_device
test32=$?
python -m unittest -v tests.test_gatt
test41=$?
python3 -m unittest -v tests.test_gatt
test42=$?
pycodestyle -v bluezero
test51=$?
pycodestyle -v examples
test52=$?
pycodestyle -v tests
test53=$?

group1=$((test11 + test12))
group2=$((test21 + test22))
group3=$((test31 + test32))
group4=$((test41 + test42))
group5=$((test51 + test52 + test53))
if [ $((group1 + group2 + group3 + group4 + group5)) -ne 0 ]; then
   echo -e "\n\n###  A test has failed!!  ###\n"
else
    echo -e "\n\nSuccess!!!\n"
fi
