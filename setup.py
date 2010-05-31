# -*- coding: utf-8 -*-
"""
==========
rdreiflask
==========

The new, fancy rdrei.net micro portal.
Online version at `rdrei.net <http://rdrei.net/>`_.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from setuptools import setup, find_packages


setup(
    name="rdreiflask",
    version="0.0.1-git",
    packages=(
        'rdrei',
        'rdrei.views',
        'rdrei.utils'),
    package_data={
        'rdrei': [
            'templates/**.html',
            'static/*']},
    author="Pascal Hartig",
    author_email="phartig@weluse.de",
    description="rdrei micro portal",
    long_description=__doc__,
    license="GPL",
    keywords="portal homepage",
    url="http://rdrei.net/",
    test_require="nose",
    test_suite="nose.collector")
