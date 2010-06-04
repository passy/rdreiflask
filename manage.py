#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
"""
rdreiflask.manage
~~~~~~~~~~~~~~~~~

Management script.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from werkzeug import script


def _prepare_context(app):
    ctx = app.test_request_context()
    ctx.push()
    app.preprocess_request()

    return ctx


def action_runserver():
    from rdrei.application import app

    app.run(debug=True, host="0.0.0.0")


def action_flickr_import():
    from rdrei.application import app
    from rdrei.utils.redis_db import open_connection
    from rdrei.utils import flickr

    # Without this, redis is not initialized.
    db = open_connection()

    for photo in flickr.get_recent_profile_photos():
        # Check if the entry exists.
        key = 'photo:' + photo['id']
        print("Current Key: ", key)
        if db.exists(key):
            print("Came across already known photo.")
            break

        for subkey in ('title', 'farm', 'server', 'secret', 'id',
                       'original_secret', 'height_o', 'width_o',
                       'height_m', 'width_m'):
            # We need to double-check, because flickr is very picky about what
            # and when to include attributes.
            if subkey in photo:
                db.hset(key, subkey, photo[subkey])

        # Save the tags to subsets
        for tag in photo['tags'].split(' '):
            db.sadd('phototags:' + tag, photo['id'])
            # And don't forget to keep track of the tags itself.
            db.sadd('phototags', tag)

        db.sadd('photos', photo['id'])




def action_dump_photos():
    """
    Dumps the photos from redis to stdout.
    """
    import simplejson
    from flask import g
    from rdrei.application import app
    from rdrei.utils.redis_fixtures import dump_fixture
    ctx = _prepare_context(app)


    # As 'closure' to not load simplejson in global space.
    class _SetSerializer(simplejson.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)

            return simplejson.JSONEncoder.default(self, obj)


    result = []
    result.append(dump_fixture("photos"))

    for photo in g.db.smembers("photos"):
        result.append(dump_fixture("photo:" + photo))

    result.append(dump_fixture("phototags"))

    for phototag in g.db.smembers("phototags"):
        result.append(dump_fixture("phototags:" + phototag))

    print(simplejson.dumps(result, cls=_SetSerializer))

    ctx.pop()


def action_dump_albums():
    """Dumps the albums to stdout."""

    import simplejson
    from flask import g
    from rdrei.application import app
    from rdrei.utils.redis_fixtures import dump_fixture

    ctx = _prepare_context(app)

    result = []
    result.append(dump_fixture("photoalbum"))

    for i in xrange(1, int(g.db.get("photoalbum"))):
        key = "photoalbum:" + str(i)
        if g.db.exists(key):
            result.append(dump_fixture(key))

    print(simplejson.dumps(result))

    ctx.pop()


def action_load_dump(filename="data.json"):
    """Loads a fixture from a file."""

    from rdrei.utils.redis_fixtures import load_fixture
    ctx = _prepare_context(app)

    load_fixture(filename)

    ctx.pop()


if __name__ == '__main__':
    script.run()
# vim: set ts=8 sw=4 tw=78 ft=python:
