#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup, find_packages

install_requires = ['jsonpickle','ujson','pycrypto','DBUtils','jinja2','MySQL_python','pyOpenSSL','Twisted','zope.interface','protobuf']
    
kws = {'install_requires': install_requires}

setup(
    name = "common",
    version = '0.0.2',

    packages = find_packages(),
    include_package_data = True,
    zip_safe=False,
    author = "Behill",
    author_email = "joost@cassee.net",
    description = "A Common tools for twisted", 
    long_description = 'common package',
    license = "MIT License",
    keywords = "python twisted",
    platforms = ['any'],
    **kws
)
