# -*- coding: utf-8 -*-
"""
rdrei.utils.redis
~~~~~~~~~~~~~~~~~

Redis helper utils.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from redis import Redis
from rdrei import settings


def open_connection(database=None):
    """
    Opens a connection to a redis database based on config values but
    accepts an optional ``database`` parameter to override the config
    value.
    """
    if database is None:
        database = settings.REDIS_DB

    return Redis(settings.REDIS_HOST, settings.REDIS_PORT,
                 database)
