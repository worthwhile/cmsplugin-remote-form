#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import join, dirname
import sys
import cmsplugin_remote_form

from setuptools import setup, find_packages


def long_description():
    try:
        return open(join(dirname(__file__), 'README.md')).read()
    except IOError:
        return "LONG_DESCRIPTION Error"

version = cmsplugin_remote_form.__version__

setup(
    name='cmsplugin_contact_plus',
    version=version,
    packages=find_packages(),
    license='BSD License',
    url='https://github.com/worthwhile/cmsplugin-remote-form/',
    description='A django CMS plugin to dynamically create forms to hit remote endpoints.',
    long_description=long_description(),
    author='Worthwhile',
    author_email='admin@arteria.ch',
    # TODO: add others
    install_requires=open('requirements.txt').read().splitlines(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
    ],
)
