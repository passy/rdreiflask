# -*- coding: utf-8 -*-
"""
application
~~~~~~~~~~~

Main entry point for for rdrei.net.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import Flask, g, session
from rdrei import settings, __version__

app = Flask('rdrei')
app.config.from_object(settings)

from rdrei.utils import redis_db
from rdrei.views.photos import photos
from rdrei.views.admin import admin

app.register_module(photos)
app.register_module(admin)


@app.before_request
def _set_template_vars():
    """Make debug mode and version available to the template."""
    g.debug = settings.DEBUG
    g.version = __version__

@app.before_request
def _open_redis():
    g.db = redis_db.open_connection()


@app.before_request
def _check_login():
    """
    Sets g.logged_in to true if the user is logged in via twitter and
    matches a user name defined in ``settings.ADMIN_USERS``.
    """

    if session.get('twitter_user', None) in settings.ADMIN_USERS:
        g.is_admin = True
    else:
        g.is_admin = False


@app.after_request
def _close_redis(response):
    g.db.connection.disconnect()
    return response
