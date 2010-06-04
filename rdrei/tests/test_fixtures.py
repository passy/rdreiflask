# -*- coding: utf-8 -*-
"""
tests.test_fixtures
~~~~~~~~~~~~~~~~~~~

Test the fixture support.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: BSD
"""

from nose.tools import eq_
from rdrei.utils.redis_fixtures import load_fixture
from rdrei.utils import redis_db
from os.path import dirname, join, abspath


def get_fixture_path(name):
    """Returns the absolute path to a fixture file."""

    return abspath(join(
        dirname(__file__),
        "fixtures",
        name))


class TestRedisFixtures(object):

    def __init__(self):
        # Open the test database
        self.redis_db = redis_db.open_connection(1)

    def __del__(self):
        # Wipe the test database.
        self.redis_db.flushdb()

    def test_load_single_key(self):
        # This should not be available, yet.
        assert self.redis_db.get('hello') is None
        fixture = load_fixture(self.redis_db,
                               get_fixture_path("0001_simple_key.json"))
        eq_(self.redis_db.get('hello'), "world")
