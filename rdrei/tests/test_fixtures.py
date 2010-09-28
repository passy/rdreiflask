# -*- coding: utf-8 -*-
"""
tests.test_fixtures
~~~~~~~~~~~~~~~~~~~

Test the fixture support.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: BSD
"""

from nose.tools import eq_
from flask import g
from rdrei.tests.utils import get_fixture_path
from rdrei.application import create_app
from rdrei.utils.redis_fixtures import load_fixture
from rdrei.utils import redis


class TestRedisFixtures(object):
    """Tests for the redis fixture module. This relies on a huge amount of
    hard-coded data that can be found in the fixtures.
    """

    __test__ = True

    def __init__(self):
        """Open the test database."""
        self.app = create_app()
        self.request_context = self.app.test_request_context()
        self.request_context.push()
        self.app.preprocess_request()
        self.redis_db = g.db

    def __del__(self):
        """Wipe the test database."""
        self.redis_db.flushdb()
        self.request_context.pop()

    def test_load_single_key(self):
        """Load a single key into the DB."""
        self.redis_db.flushdb()

        # This should not be available, yet.
        assert self.redis_db.get('hello') is None
        load_fixture(get_fixture_path("0001_simple_key.json"))
        eq_(self.redis_db.get('hello'), "world")

    def test_load_multiple_keys(self):
        load_fixture(get_fixture_path("0002_multiple_keys.json"))

        eq_(self.redis_db.get('hello'), "world")
        eq_(self.redis_db.lindex('mylist', 0), "item1")
        eq_(self.redis_db.lindex('mylist', 1), "item2")
        eq_(self.redis_db.hget('myhash', "key1"), "val1")

    def test_load_old_photos(self):
        """Tests the import of the old photos."""

        load_fixture(get_fixture_path("0000_old_photos.json"))

        assert '650438865' in self.redis_db.smembers('phototags:kiwo072')
