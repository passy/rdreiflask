# -*- coding: utf-8 -*-
"""
rdrei.tests.functional
~~~~~~~~~~~~~~~~~~~~~~

Functional tests

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from nose.tools import eq_
from rdrei.application import app


class TestPhotosModule(object):
    """Tests the photos pages."""

    __test__ = True

    def __init__(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/photos')
        # It's moved.
        eq_(response.status_code, 301)

        response = self.app.get('/photos/')
        eq_(response.status_code, 200)
        assert "<h2>Foto-Alben</h2>" in response.data

    def test_album(self):
        response = self.app.get('/photos/album/1')
        eq_(response.status_code, 200)

    def test_details(self):
        response = self.app.get('/photos/album/1/2765702228')
        eq_(response.status_code, 200)

    def test_album_404(self):
        response = self.app.get('/photos/album/999999999999999')
        eq_(response.status_code, 404)

    def test_album_photo_404(self):
        """Test if a non-existant photo raises a 404."""
        response = self.app.get('/photos/album/1/124')
        eq_(response.status_code, 404)

    def test_album_photo_404_2(self):
        """Test if an existing photo raises a 404 in a wrong album."""
        response = self.app.get('/photos/album/1/2771608178')
        eq_(response.status_code, 404)
        assert "Photo exists, but you're looking in the wrong place." in \
                response.data


class TestBaseModule():
    """Tests the views not associated to a module."""

    def __init__(self):
        self.app = app.test_client()

    def test_frontpage(self):
        response = self.app.get('/')
        eq_(response.status_code, 200)
