#!/usr/bin/env bash
python -m unittest -v tests.test_url_to_hex
python3 -m unittest -v tests.test_url_to_hex
python -m unittest -v tests.test_adapter
python3 -m unittest -v tests.test_adapter
python -m unittest -v tests.test_device
python3 -m unittest -v tests.test_device
pep8 bluezero
pep8 --ignore=E402 examples
pep8 tests
