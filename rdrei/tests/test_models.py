# -*- coding: utf-8 -*-
"""
rdrei.tests.test_models
~~~~~~~~~~~~~~~~~~~~~~~

Nose tests for the redis 'models'. Heavily relies on my local test data where
I have no fixtures for. This is a TODO.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""


from rdrei.models import Photos, PhotoAlbums
from rdrei.utils import redis_db
from rdrei.application import app
from flask import g
from contextlib import contextmanager


@contextmanager
def _request_context(*args, **kwargs):
    """Provides a request with redis initialized."""

    with app.test_request_context(*args, **kwargs):
        # Unfortunately, flask does not provide decorated before/after
        # functions in this context, so we have to do this manually.
        g.db = redis_db.open_connection()
        yield


class TestPhotos(object):
    """Tests the Photos model."""

    def __init__(self):
        """Initializes the redis db."""

        self.app = app.test_client()


    def test_basic_query(self):
        """Tests a basic photo query."""

        counter = 0
        with _request_context('/'):
            for photo in Photos.by_tag("strand050708"):
                counter += 1

        assert counter > 0, "No photos yielded."

    def test_photo_object(self):
        """Tests photo object."""

        with _request_context('/'):
            photo = Photos.by_id(2765703256)

            assert photo.title == "Jan"
            assert photo.id == "2765703256"
            assert photo.url.small_square == "http://farm4.static.flickr.com/3156/2765703256_1e70b3f475_s.jpg"


class TestPhotoAlbums(object):
    """Tests for the photo album model."""

    def test_next(self):
        """Tests the next methods."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            next_list = list(album.next_photos('2765703772', 5))

            assert len(next_list) == 5
            assert next_list[0].id == '2764855853'
            assert next_list[4].id == '2765704162'

    def test_next_truncated(self):
        """Test next if above the upper limit."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            next_list = list(album.next_photos('2765703256', 4))

            assert len(next_list) == 2
            assert next_list[0].id == '2765703092'
            assert next_list[1].id == '2765702000'

    def test_prev(self):
        """Tests the prev method."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            prev_list = list(album.previous_photos('2765703256', 4))

            assert len(prev_list) == 4
            assert prev_list[0].id == '2765702488'
            assert prev_list[3].id == '2765704378'

    def test_prev_truncated(self):
        """Tests the prev method with truncated result set."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            prev_list = list(album.previous_photos('2765703772', 4))

            assert len(prev_list) == 1
            assert prev_list[0].id == '2765702228'

    def test_empty_next(self):
        """Tests what happens with a next on the last element."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            next_list = list(album.next_photos('2765702000'))

            assert len(next_list) == 0
