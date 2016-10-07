====================
Notes For Developers
====================



Build pypi package
------------------

Update version information in setup.py.

To upload to pypi:

.. code-block:: none

    python3 setup.py sdist bdist_wheel upload -r pypi


Build Documentation
-------------------

Update version information in docs/conf.py:

.. code-block:: none

    cd docs
    make clean
    make html
    cd ..
    python3 setup.py upload_docs --upload-dir docs/_build/html

