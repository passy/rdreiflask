# -*- coding: utf-8 -*-
"""
application
~~~~~~~~~~~

Main entry point for for rdrei.net.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import Flask, g, session
from rdrei import settings

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
app.debug = settings.DEBUG

from rdrei.utils import redis_db


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


import rdrei.views
