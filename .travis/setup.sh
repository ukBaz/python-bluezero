#!/bin/bash
case "${TRAVIS_PYTHON_VERSION}" in
    2.7)
        # Sort out loading of python modules
        echo $PYTHONPATH
        echo $PATH
        python -c "import site; print(site.getsitepackages())"
        ;;
    3.3)
        echo $PYTHONPATH
        echo $PATH
        python3 -c "import site; print(site.getsitepackages())"
        ;;
esac