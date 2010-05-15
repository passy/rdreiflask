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
from werkzeug.exceptions import NotFound


@app.route("/photos")
@templated("photos/index.html")
def photo_index():
    albums = PhotoAlbums.all()
    return {'albums': albums}


@app.route("/photos/album/<int:album_id>")
@templated("photos/album.html")
def photo_album(album_id):

    return {
        'photos': Photos.all_by_album(album_id),
        'album': PhotoAlbums.by_id(album_id)
    }

@app.route("/photos/album/<int:album_id>/<int:photo_id>")
@templated("photos/details.html")
def photo_details(album_id, photo_id):
    """
    Shows display about a single photo. The ``album_id`` is used for
    next and previous photos as well as back links.
    """

    album = PhotoAlbums.by_id(album_id)
    photo = Photos.by_id(photo_id)

    if not any([album, photo]):
        raise NotFound("Either album or photo could not be found.")

    return {
        'photo': photo,
        'title': album['name'] + u' \u2014 ' + photo.title
    }
