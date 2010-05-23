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
from flask import url_for


class TestPhotosModule():
    """Tests the photos pages."""

    def __init__(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/photos')
        # It's moved.
        eq_(response.status_code, 301)

        response = self.app.get('/photos/')
        eq_(response.status_code, 200)
        assert "<h2>Photos</h2>" in response.data

    def test_album(self):
        response = self.app.get('/photos/album/1')
        eq_(response.status_code, 200)

    def test_details(self):
        response = self.app.get('/photos/album/1/2765702228')
        eq_(response.status_code, 200)
