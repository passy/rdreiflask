# -*- coding: utf-8 -*-
"""
rdrei.views.photos
~~~~~~~~~~~~~~~~~~

Photo related views.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from rdrei.application import app
from rdrei.models import Photos, PhotoAlbums
from rdrei.utils.template import render_template, templated


@app.route("/photos")
@templated("photos/index.html")
def photo_index():
    albums = PhotoAlbums.all()
    return {'albums': albums}


@app.route("/photos/<int:album_id>")
@templated("photos/details.html")
def photo_details(album_id):

    return {'photos': Photo.all_by_album(album_id)}
