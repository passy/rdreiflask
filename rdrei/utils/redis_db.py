# -*- coding: utf-8 -*-
"""
rdrei.utils.redis
~~~~~~~~~~~~~~~~~

Redis helper utils.
Actually, this entire file has some really bad smell because of its insane
amount of import time side effects. But this is part of the nature of flask
and I guess that's okay for a project of this small scale.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from redis import Redis
from flask import g

from rdrei.application import app
from rdrei import settings


def open_connection():
    return Redis(settings.REDIS_HOST, settings.REDIS_PORT,
                       settings.REDIS_DB)

@app.before_request
def before_request():
    g.db = open_connection()


@app.after_request
def after_request(response):
    g.db.connection.disconnect()
    return response

def get_db():
    return g.db
