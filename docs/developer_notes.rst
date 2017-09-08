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
* `git tag` with version number
* Check read the docs page


Specifics on some steps
=======================

Build pypi package
------------------

Update version information in setup.py.

To upload to pypi:

.. code-block:: none

    python3 setup.py bdist_wheel sdist
    twine upload  dist/*


Test Build of Documentation
---------------------------

Update version information in docs/conf.py:

.. code-block:: none

    cd docs
    make clean
    make html

* readthedocs gets update from GitHub
* readthedocs versions are based on GitHub version tags
