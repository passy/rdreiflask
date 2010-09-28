# -*- coding: utf-8 -*-
"""
rdrei.tests.test_models
~~~~~~~~~~~~~~~~~~~~~~~

Nose tests for the redis 'models'. Heavily relies on my local test data where
I have no fixtures for. This is a TODO.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""


from rdrei.models import Photos, PhotoAlbums, PhotoNotFoundError
from rdrei.tests.utils import get_fixture_path
from rdrei.utils.redis_fixtures import load_fixture
from rdrei.utils import redis
from rdrei.application import create_app
from flask import g
from contextlib import contextmanager
from nose.tools import raises


@contextmanager
def _request_context(*args, **kwargs):
    """Provides a request with redis initialized."""

    app = create_app()
    with app.test_request_context(*args, **kwargs):
        app.preprocess_request()
        load_fixture(get_fixture_path("0010_photos.json"))
        load_fixture(get_fixture_path("0011_photo_albums.json"))
        yield


class TestPhotos(object):
    """Tests the Photos model."""

    __test__ = True

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
            assert photo.url.small_square == \
            "http://farm4.static.flickr.com/3156/2765703256_1e70b3f475_s.jpg"

    def test_original_dimensions(self):
        """Tests the original dimensions."""

        with _request_context('/'):
            photo = Photos.by_id(2771566478)

            assert photo.title == "Anna, Julia"
            assert photo.url.original == \
            "http://farm4.static.flickr.com/3161/2771566478_de1bd165a0_o.jpg"
            assert photo.horizontal == False
            assert int(photo.height_o) == 768

            photo2 = Photos.by_id(2771569486)
            assert photo2.horizontal == True
            assert int(photo2.height_o) == 1024


class TestPhotoAlbums(object):
    """Tests for the photo album model."""

    __test__ = True

    def test_next(self):
        """Tests the next methods."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            next_list = list(album.next_photos('2765702228', 5))

            assert len(next_list) == 5
            assert next_list[0].id == '2764854905'
            assert next_list[4].id == '2765704378'

    def test_next_truncated(self):
        """Test next if above the upper limit."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            next_list = list(album.next_photos('2765703772', 4))

            assert len(next_list) == 2
            assert next_list[0].id == '2765702000'
            assert next_list[1].id == '2765703092'

    def test_prev(self):
        """Tests the prev method."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            prev_list = list(album.previous_photos('2765703256', 4))

            assert len(prev_list) == 4
            assert prev_list[0].id == '2764854737'
            assert prev_list[3].id == '2765704162'

    def test_prev_truncated(self):
        """Tests the prev method with truncated result set."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            prev_list = list(album.previous_photos('2764854905', 4))

            assert len(prev_list) == 1
            assert prev_list[0].id == '2765702228'

    def test_empty_next(self):
        """Tests what happens with a next on the last element."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            next_list = list(album.next_photos('2765703092'))

            assert len(next_list) == 0

    @raises(PhotoNotFoundError)
    def test_access_photo_not_in_album(self):
        """Access a photo that is not in an album."""

        with _request_context('/'):
            album = PhotoAlbums.by_id(1)
            prev_photo = album.previous_photo('2771608178')
