# -*- coding: utf-8 -*-
"""
rdrei.tests.utils
~~~~~~~~~~~~~~~~~

Utils for testing.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""
from os.path import dirname, join, abspath


def get_fixture_path(name):
    """Returns the absolute path to a fixture file."""

    return abspath(join(
        dirname(__file__),
        "fixtures",
        name))
