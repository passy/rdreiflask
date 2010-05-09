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
        if db.type(key) != 'none':
            print("Came across already known photo.")
            break

        for subkey in ('title', 'farm', 'server', 'secret', 'id'):
            db.hset(key, subkey, photo[subkey])

        db.lpush('photos', photo['id'])

if __name__ == '__main__':
    script.run()
# vim: set ts=8 sw=4 tw=78 ft=python: 
