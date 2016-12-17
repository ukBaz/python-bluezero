====================
Notes For Developers
====================

Release Checklist
=================

* Check Travis-tests are passing
* Update version info in setup.py
* Build and publish pypi package
* Check pypi page for obvious errors
* Update version in docs/conf.py
* Build and publish project documentation
* Check read the docs page
* `git tag` with version number


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

