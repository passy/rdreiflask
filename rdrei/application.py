# -*- coding: utf-8 -*-
"""
application
~~~~~~~~~~~

Main entry point for for rdrei.net.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import Flask, g
app = Flask(__name__)

from rdrei.utils import redis_db


@app.before_request
def before_request():
    g.db = redis_db.open_connection()


@app.after_request
def after_request(response):
    g.db.connection.disconnect()
    return response


import rdrei.views
