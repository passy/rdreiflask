# -*- coding: utf-8 -*-
"""
rdrei.models
~~~~~~~~~~~~

Model-ish adapters for the redis store.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import g
from rdrei import settings
from werkzeug.utils import cached_property


class FlickrURL(object):
    """Converts a photo to a URL."""

    _SIZE_MAPPING = {
        'small_square': '_s',
        'thumb': '_t',
        'small': '_m',
        'medium': '',
        'large': '_b',
        'original': '_o'}

    def __init__(self, photo):
        self.photo = photo

    def __getattr__(self, method):
        """
        Allows access to flickr url in an easy manner. Like
        photo = Photo.by_id(123)
        url = photo.url.thumb
        """
        if method in self._SIZE_MAPPING:
            return "http://farm{farm_id}.static.flickr.com/" \
                   "{server}/{id}_{secret}{size}.jpg".format(
                farm_id=self.photo.farm,
                server=self.photo.server,
                id=self.photo.id,
                secret=self.photo.secret,
                size=self._SIZE_MAPPING[method])
        else:
            return object.__getattr__(method)

    @property
    def details(self):
        """Returns the details url for the photo."""

        return "http://flickr.com/photos/{username}/{photo_id}/".format(
            username=settings.FLICKR_USER_NAME,
            photo_id=self.photo.id)


class BaseModel(object):
    """Base for all models."""

    def __init__(self, data):
        self.__dict__ = data

    def get_key(self):
        """Returns a key for the current entry."""

        return ":".join([self.__prefix__, str(self.id)])

    def _save_hash(self):
        """Saves all data to redis. Naive implementation."""

        if 'id' not in self.__dict__:
            # Create a new id.
            self.id = g.db.incr("photoalbum")

        return self._save_existing_hash()

    def _save_existing_hash(self):
        """Update an existing hash entry."""
        for key, value in self.__dict__.iteritems():
            if key == 'id':
                continue
            g.db.hset(self.get_key(), key, value)

    def __len__(self):
        return len(self.__dict__)


class Photo(BaseModel):
    """
    Object representation of a photo.
    """

    @property
    def url(self):
        # Create the url object on the fly.
        return FlickrURL(self)

    def __repr__(self):
        return '<Photo(id={0}, title="{1}")>'.format(
            self.id,
            self.title)


class Photos(object):
    """
    Access to collections of photos.
    """

    @staticmethod
    def by_id(id):
        return Photo(g.db.hgetall("photo:" + str(id)))

    @staticmethod
    def by_tag(tagname):
        ids = g.db.smembers('phototags:' + tagname)
        for id in ids:
            yield Photos.by_id(id)

    @staticmethod
    def all_by_album(id):
        tagname = PhotoAlbums.by_id(id, "tag")
        return Photos.by_tag(tagname)

    @staticmethod
    def tags():
        return g.db.smembers('phototags')


class PhotoAlbum(BaseModel):
    """
    Object representation of a single album.
    """

    __prefix__ = "photoalbum"

    @cached_property
    def photos(self):
        return g.db.smembers("phototags:" + self.tag)

    @cached_property
    def frontcover_photo(self):
        """
        Property that returns either an instance of :class:``Photo`` or
        ``None`` as this is an optional attribute.
        """
        if 'frontcover' in self.__dict__:
            return Photos.by_id(self.frontcover)

    def next_photos(self, photo_id, count=1):
        """
        Returns the next ``count`` photo elements after the photo identified
        by ``photo_id``.
        """

        photos = list(self.photos)
        index = photos.index(str(photo_id)) + 1
        upper_index = min(index + count, len(photos))
        element_ids = photos[index:upper_index]

        for id in element_ids:
            yield Photos.by_id(id)

    def next_photo(self, photo_id):
        try:
            return self.next_photos(photo_id).next()
        except StopIteration:
            return None

    def previous_photos(self, photo_id, count=1):
        """
        See :meth:``next``.
        """

        photos = list(self.photos)
        index = photos.index(str(photo_id))
        lower_index = max(0, index - count)
        element_ids = photos[lower_index:index]
        element_ids.reverse()

        for id in element_ids:
            yield Photos.by_id(id)

    def previous_photo(self, photo_id):
        try:
            return self.previous_photos(photo_id).next()
        except StopIteration:
            return None

    def save(self):
        return self._save_hash()


class PhotoAlbums(object):
    """Access to photo albums."""

    @staticmethod
    def by_id(id, attribute=None):
        """Find a photoalbum by its id."""

        key = "photoalbum:" + str(id)

        if attribute:
            return g.db.hget(key, attribute)
        else:
            album = g.db.hgetall(key)
            if album is not None:
                album['id'] = id
                return PhotoAlbum(album)

    @staticmethod
    def exists():
        """
        Checks whether the PhotoAlbum data structures exist.
        """

        return g.db.exists("photoalbum")

    @staticmethod
    def all(offset=1, limit=None, attribute=None):
        """
        Get all albums with by an optional offset of ``offset`` and a
        maximum result size of ``limit``.
        Remember the starting value is 1 not 0!
        """
        if limit is None:
            album_count = g.db.get("photoalbum")
            limit = int(album_count) - (offset - 1)

        for i in xrange(offset, offset + limit):
            key = "photoalbum:" + str(i)
            if not g.db.exists(key):
                continue

            if attribute:
                result = g.db.hget(key, attribute)
            else:
                result = g.db.hgetall(key)
                # This could be useful.
                result['id'] = i

            # Make sure, we're not yielding a deleted entry.
            if result:
                yield PhotoAlbum(result)


class PhotoAlbumNotFoundError(Exception):
    pass
