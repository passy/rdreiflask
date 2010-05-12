# -*- coding: utf-8 -*-
"""
rdrei.models
~~~~~~~~~~~~

Model-ish adapters for the redis store.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import g

class FlickrURL(object):
    """Converts a photo to a URL."""

    _SIZE_MAPPING = {
        'small_square': '_s',
        'thumb': '_t',
        'small': '_m',
        'medium': '',
        'large': '_b',
        'original': '_o'
    }

    _BASE_URL = "http://static.flickr.com/"

    def __init__(self, photo):
        self.photo = photo

    def __getattr__(self, method):
        """
        Allows access to flickr url in an easy manner. Like
        photo = Photo.by_id(123)
        url = photo.url.thumb
        """
        if method in self._SIZE_MAPPING:
            return "{base_url}/{server}/{id}_{secret}{size}.jpg".format(
                base_url=self._BASE_URL,
                server=self.photo.server,
                id=self.photo.id,
                secret=self.photo.secret,
                size=self._SIZE_MAPPING[method]
            )
        else:
            return object.__getattr__(method)


class Photo(object):
    """
    Object representation of a photo.
    """

    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.farm = data['farm']
        self.server = data['server']
        self.secret = data['secret']

    @property
    def url(self):
        # Create the url object on the fly.
        return FlickrURL(self)

    def __str__(self):
        return '<Photo(id={0}, title="{1}")>'.format(
            self.id,
            self.title
        )


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


class PhotoAlbums(object):
    """
    Access to photo albums.
    """

    @staticmethod
    def by_id(id, attribute=None):
        """Find a photoalbum by its id."""

        key = "photoalbum:" + str(id)

        if attribute:
            return g.db.hget(key, attribute)
        else:
            return g.db.hgetall(key)

    @staticmethod
    def all(offset=1, limit=None, attribute=None):
        """
        Get all albums with by an optional offset of ``offset`` and a
        maximum result size of ``limit``.
        Remember the starting value is 1 not 0!
        """
        if limit is None:
            limit = int(g.db.get("photoalbum")) - (offset - 1)

        for i in xrange(offset, offset + limit):
            key = "photoalbum:" + str(i)
            if attribute:
                result = g.db.hget(key, attribute)
            else:
                result = g.db.hgetall(key)
                # This could be useful.
                result['id'] = i

            # Make sure, we're not yielding a deleted entry.
            if result:
                yield result
