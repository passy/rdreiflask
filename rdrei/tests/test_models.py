# -*- coding: utf-8 -*-
"""
rdrei.tests.test_models
~~~~~~~~~~~~~~~~~~~~~~~

Nose tests for the redis 'models'. Heavily relies on my local test data where
I have no fixtures for. This is a TODO.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""


from rdrei.models import Photos
from rdrei.utils import redis_db
from rdrei.application import app
from flask import g
from contextlib import contextmanager


class TestPhotos(object):
    """Tests the Photos model."""

    def __init__(self):
        """Initializes the redis db."""

        self.app = app.test_client()

    @contextmanager
    def _request_context(self, *args, **kwargs):
        """Provides a request with redis initialized."""

        with app.test_request_context(*args, **kwargs):
            # Unfortunately, flask does not provide decorated before/after
            # functions in this context, so we have to do this manually.
            g.db = redis_db.open_connection()
            yield

    def test_basic_query(self):
        """Tests a basic photo query."""

        counter = 0
        with self._request_context('/'):
            for photo in Photos.by_tag("strand050708"):
                counter += 1

        assert counter > 0, "No photos yielded."

    def test_photo_object(self):
        """Tests photo object."""

        with self._request_context('/'):
            photo = Photos.by_id(2765703256)

            assert photo.title == "Jan"
            assert photo.id == "2765703256"
            assert photo.url.small_square == "http://static.flickr.com//3156/2765703256_1e70b3f475_s.jpg"
