# -*- coding: utf-8 -*-
"""
rdrei.views.photos
~~~~~~~~~~~~~~~~~~

Photo related views.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from rdrei import settings
from rdrei.application import app
from rdrei.models import Photos, PhotoAlbums
from rdrei.utils.template import render_template, templated
from werkzeug.exceptions import NotFound, BadRequest


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

    if not all([album, photo]):
        raise NotFound("Either album or photo could not be found.")

    prev_photo = album.previous_photo(photo_id)
    next_photos = list(album.next_photos(photo_id,
                                    settings.PHOTOS_PRELOAD_NEXT_COUNT))
    if next_photos:
        next_photo = next_photos[0]
    else:
        next_photo = None

    return {
        'photo': photo,
        'title': album.title + u' \u2014 ' + photo.title,
        'album': album,
        'next_photo': next_photo,
        'prev_photo': prev_photo
    }

@app.route("/photos/comments/<int:album_id>/<int:photo_id>")
@templated("photos/comments.html")
def photo_comments(album_id, photo_id):
    """
    Allows comment loading in an iframe for the given ``album_id`` and
    ``photo_id``.
    """

    # Verification that the entry exists should be not required.
    try:
        album_id = int(album_id)
        photo_id = int(photo_id)
    except (ValueError, TypeError):
        raise BadRequest

    return {
        'album_id': album_id,
        'photo_id': photo_id
    }
