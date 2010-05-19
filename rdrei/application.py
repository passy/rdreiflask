# -*- coding: utf-8 -*-
"""
application
~~~~~~~~~~~

Main entry point for for rdrei.net.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import Flask, g
from rdrei import settings

app = Flask(__name__)
app.debug = settings.DEBUG
app.secret_key = settings.SECRET_KEY

from rdrei.utils import redis_db


@app.before_request
def before_request():
    g.db = redis_db.open_connection()


@app.after_request
def after_request(response):
    g.db.connection.disconnect()
    return response


import rdrei.views
