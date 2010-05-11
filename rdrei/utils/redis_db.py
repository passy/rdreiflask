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


def open_connection():
    return Redis(settings.REDIS_HOST, settings.REDIS_PORT,
                       settings.REDIS_DB)
