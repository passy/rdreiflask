#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
"""
rdreiflask.manage
~~~~~~~~~~~~~~~~~

Management script.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from contextlib import contextmanager
from flaskext.script import Manager
from rdrei.application import create_app


manager = Manager(create_app())


@contextmanager
def _prepared_context(app):
    ctx = app.test_request_context()
    ctx.push()
    app.preprocess_request()
    yield
    ctx.pop()


@manager.command
def flickr_import(app):
    """Import the latest photos to redis."""
    from flask import g
    from rdrei.utils import flickr

    with _prepared_context(app):
        for photo in flickr.get_recent_profile_photos():
            # Check if the entry exists.
            key = 'photo:' + photo['id']
            print("Current Key: ", key)
            if g.db.exists(key):
                print("Came across already known photo.")
                break

            for subkey in ('title', 'farm', 'server', 'secret', 'id',
                           'original_secret', 'height_o', 'width_o',
                           'height_m', 'width_m'):
                # We need to double-check, because flickr is very picky about
                # what and when to include attributes.
                if subkey in photo:
                    g.db.hset(key, subkey, photo[subkey])

            # Save the tags to subsets
            for tag in photo['tags'].split(' '):
                g.db.sadd('phototags:' + tag, photo['id'])
                # And don't forget to keep track of the tags itself.
                g.db.sadd('phototags', tag)

            g.db.sadd('photos', photo['id'])


@manager.command
def dump_photos(app):
    """
    Dumps the photos from redis to stdout.
    """
    import json
    from flask import g
    from rdrei.utils.redis_fixtures import dump_fixture

    # As 'closure' to not load json in global space.
    class _SetSerializer(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)

            return json.JSONEncoder.default(self, obj)

    with _prepared_context(app):
        result = []
        result.append(dump_fixture("photos"))

        for photo in g.db.smembers("photos"):
            result.append(dump_fixture("photo:" + photo))

        result.append(dump_fixture("phototags"))

        for phototag in g.db.smembers("phototags"):
            result.append(dump_fixture("phototags:" + phototag))

        print(json.dumps(result, cls=_SetSerializer))


@manager.command
def dump_albums(app):
    """Dumps the albums to stdout."""

    import json
    from flask import g
    from rdrei.utils.redis_fixtures import dump_fixture

    with _prepared_context(app):
        result = []
        result.append(dump_fixture("photoalbum"))

        for i in xrange(1, int(g.db.get("photoalbum"))):
            key = "photoalbum:" + str(i)
            if g.db.exists(key):
                result.append(dump_fixture(key))

        print(json.dumps(result))


@manager.command
def load_dump(app, filename="data.json"):
    """
    Loads a fixture from a file.

    :param filename: Filename to load the JSON dump from.
    """

    from rdrei.utils.redis_fixtures import load_fixture
    with _prepared_context(app):
        load_fixture(filename)


if __name__ == '__main__':
    manager.run()
# vim: set ts=8 sw=4 tw=78 ft=python:
