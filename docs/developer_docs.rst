=======================
Developer Documentation
=======================

Developer Install
=================

If you wish to help with the development of Bluezero then the recommended way
of installing for edit is as follows:

.. code-block::

    git clone https://github.com/ukBaz/python-bluezero.git
    cd python-bluezero
    python3 -m venv --system-site-packages venv
    . venv/bin/activate
    pip3 install -e .[dev]


.. note::

    Use of a Python Virtual environment is good practice when developing
    with Python. Because some of the dependencies for Bluezero are installed
    system-wide with `apt`, then it is necessary to use the
    `--system-site-packages` option when creating the virtual environment so
    those packages can be found.


Release Checklist
=================

* Check tests are passing (run_local_tests.sh)
* Update version info (see `Update Version Info`_)
* Build and publish PyPI package (see `Build PyPI package`_)
* Check PyPI page for obvious errors
* ``git tag`` with version number
* Check read the docs page

Update Version Info
-------------------
Use bumpversion package to update all references at once.
This library tries to use `Semantic Versioning
<https://semver.org/#semantic-versioning-200>`_

Semantic version uses three numbers that represent ``major.minor.patch``.

The bumpversion command allows you to choose which to update. In the
following example the version is being updated for a patch.

.. code-block::

    bumpversion patch setup.py


Build PyPI package
------------------

Update version information in setup.py.

To upload to PyPI:

.. code-block::

    python3 setup.py bdist_wheel sdist
    twine upload dist/*


Test Build of Documentation
---------------------------

Do a test build of the documentation and then a visual inspection.
To do a local build of the documentation:

.. code-block::

    cd docs
    make clean
    make html

* readthedocs gets update from GitHub
* readthedocs versions are based on GitHub version tags
