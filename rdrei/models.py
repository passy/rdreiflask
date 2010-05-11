# -*- coding: utf-8 -*-
"""
rdrei.models
~~~~~~~~~~~~

Model-ish adapters for the redis store.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import g


class Photos(object):
    """
    Access to collections of photos.
    """

    @staticmethod
    def by_id(id):
        return g.db.hgetall("photo" + id)

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

        key = "photoalbum:" + id

        if attribute:
            g.db.hget(key, attribute)
        else:
            return g.db.hgetall(key)

    @staticmethod
    def all(offset=0, limit=None, attribute=None):
        """
        Get all albums with by an optional offset of ``offset`` and a
        maximum result size of ``limit``.
        """
        if limit is None:
            limit = int(g.db.get("photoalbum")) - offset

        for i in xrange(offset, offset + limit):
            key = "photoalbum:" + str(i)
            if attribute:
                result = g.db.hget(key, attribute)
            else:
                result = g.db.hgetall(key)

            # Make sure, we're not yielding a deleted entry.
            if result:
                yield result
