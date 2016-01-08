__author__ = 'barry'
import os
from setuptools import setup

install_requires = []
tests_require = []

base_dir = os.path.dirname(os.path.abspath(__file__))

version = "0.0.1"

setup(
    name='bluezero',
    version=version,
    description="A library that makes using Bluez DBus API easier and more convenient",
    long_description="\n\n".join([
        open(os.path.join(base_dir, "README.rst"), "r").read(),
    ]),
    url='http://github.com/ukBaz/python-bluezero',
    author='Barry Byford',
    author_email='barry_byford@yahoo.co.uk',
    maintainer='Barry Byford',
    maintainer_email='barry_byford@yahoo.co.uk',
    packages=['bluezero'],
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="tests.get_tests",
)
