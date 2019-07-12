import sys
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name='django-verified-email',
    version='0.1.1',
    description='Verified email changes for django',
    long_description=long_description,
    license='BSD',
    packages=['verified_email_change'],
    install_requires=[
        'Django>=1.7',
        'django-ogmios',
        'django-decoratormixins',
        'django-absoluteuri',
    ],
    cmdclass={'test': PyTest},
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-django',
    ],
    package_data={
        '': ['templates/**/*.html'],
    },
)
