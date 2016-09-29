#!/usr/bin/env bash
python -m unittest -v tests.test_url_to_hex
python3 -m unittest -v tests.test_url_to_hex
python -m unittest -v tests.test_adapter
python3 -m unittest -v tests.test_adapter
python -m unittest -v tests.test_device
python3 -m unittest -v tests.test_device
pycodestyle -v bluezero
pycodestyle -v --ignore=E402 examples
pycodestyle -v tests
