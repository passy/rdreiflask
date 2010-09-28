# -*- coding: utf-8 -*-
"""
rdrei.views.photos
~~~~~~~~~~~~~~~~~~

Photo related views.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from rdrei.models import Photos, PhotoAlbums
from rdrei.utils.template import templated
from rdrei.utils.disqus_utils import get_num_posts_by_identifier
from rdrei.utils.thirdparty.disqus import APIError
from flask import g, current_app, Module
from werkzeug.exceptions import NotFound, BadRequest


photos = Module(__name__, url_prefix="/photos")


@photos.route("/")
@templated("photos/index.html")
def index():
    if PhotoAlbums.exists():
        albums = PhotoAlbums.all()
    else:
        albums = []

    return {'albums': albums}


@photos.route("/album/<int:album_id>")
@templated("photos/album.html")
def album(album_id):

    album = PhotoAlbums.by_id(album_id)
    if album is None:
        raise NotFound("Album does not exist.")

    return {
        'photos': Photos.all_by_album(album_id),
        'album': album}


@photos.route("/album/<int:album_id>/<int:photo_id>")
@templated("photos/details.html")
def details(album_id, photo_id):
    """
    Shows display about a single photo. The ``album_id`` is used for
    next and previous photos as well as back links.
    """

    album = PhotoAlbums.by_id(album_id)
    photo = Photos.by_id(photo_id)

    if not all([album, photo]):
        raise NotFound("Either album or photo could not be found.")

    if photo not in album:
        raise NotFound("Photo exists, but you're looking in the wrong place.")

    prev_photo = album.previous_photo(photo_id)
    next_photos = list(album.next_photos(
        photo_id,
        current_app.config['PHOTOS_PRELOAD_NEXT_COUNT']))
    if next_photos:
        next_photo = next_photos[0]
    else:
        next_photo = None

    return {
        'photo': photo,
        'title': album.title + u' \u2014 ' + photo.title,
        'album': album,
        'next_photo': next_photo,
        'prev_photo': prev_photo}


@photos.route("/comments/<int:album_id>/<int:photo_id>")
@templated("photos/comments.html")
def comments(album_id, photo_id):
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
        'photo_id': photo_id}


@photos.route("/num_comments/<int:photo_id>")
def num_comments(photo_id):
    """
    Returns the number of comments for the given ``photo_id``.
    The results are cached with redis and have an expiration of five minutes.
    """

    photo_id = str(photo_id)

    def _request():
        """
        Do a request and catch HTTP 500 errors that disqus randomly spits
        out.
        """
        try:
            result = get_num_posts_by_identifier("photo:" + photo_id)
        except APIError:
            result = 0

        return str(result)

    db = g.db
    cache_key = "photo_num_comments:" + photo_id

    result = db.get(cache_key)
    if result is None:
        result = _request()
        db.set(cache_key, result)
        # Maybe I could move that to the settings.
        db.expire(cache_key, 5 * 60)

    return result
