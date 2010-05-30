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

if __name__ == '__main__':
    script.run()
# vim: set ts=8 sw=4 tw=78 ft=python:
