# -*- coding: utf-8 -*-
"""
rdrei.utils.redis
~~~~~~~~~~~~~~~~~

Redis helper utils.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from __future__ import unicode_literals, print_function, absolute_import
from redis import Redis
from rdrei import settings


def open_connection(host="localhost", port=6379, database=0):
    """
    Opens a new redis connection connection for the given ``host``, ``port``
    and ``database`` parameters. Defaults to database 0 on localhost:6379.
    """
    if database is None:
        database = 0

    return Redis(host or "localhost",
                 port or 6379,
                 database)
