from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-verified-email',
    version='0.1.0',
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
)
