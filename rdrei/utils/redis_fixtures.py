# -*- coding: utf-8 -*-
"""
redis_fixtures
~~~~~~~~~~~~~~

Loading data into redis from JSOM files.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: BSD
"""

from flask import g
import simplejson


class RedisDataLoader(object):
    """
    Base class for loading a data type into redis.
    """

    def __init__(self, redis_db):
        self.redis_db = redis_db

    def save(self, key, value):
        raise NotImplementedError()


class RedisStringLoader(RedisDataLoader):
    """
    Saves a single string into redis.
    """

    def save(self, key, value):
        if not isinstance(value, basestring):
            raise TypeError("{0} is not a string!".format(key))

        self.redis_db.set(key, value)


class RedisHashLoader(RedisDataLoader):
    """
    Saves a hash into the redis db.
    """

    def save(self, key, value):
        if not isinstance(value, dict):
            raise TypeError("{0} is not a dict!".format(key))

        for hkey, hvalue in value.iteritems():
            self.redis_db.hset(key, hkey, hvalue)


class RedisSetLoader(RedisDataLoader):
    """
    Saves a set into the redis db.
    """

    def save(self, key, value):
        if isinstance(value, (list, set)):
            for entry in value:
                self.redis_db.sadd(key, entry)
        else:
            self.redis_db.sadd(key, str(value))


class RedisListLoader(RedisDataLoader):
    """
    Loads a list into redis.
    """

    def save(self, key, value):
        if not isinstance(value, list):
            raise TypeError("{0} is not a list!".format(key))

        for entry in value:
            self.redis_db.rpush(key, entry)


_REDIS_LOADER_MAPPING = {
    'string': RedisStringLoader,
    'hash': RedisHashLoader,
    'list': RedisListLoader,
    'set': RedisSetLoader}


def load_fixture(filename):
    """
    Loads a JSON fixture into redis. Accepts a JSON list like::
        [{
            "type": "string",
            "key": "hello",
            "value": "world"
        }, {
            "type": "list",
            "key": "mylist",
            "value": ["item1", "item2", "item3"]
        }, {
            "type": "hash",
            "key": "myhash",
            "value": {"key1": "val1", "key2": "val2"}
        }]

    :param filename: Path to the fixture json file.
    """

    json_data = simplejson.load(open(filename, 'r'))
    # Create a new pipeline for 'transactional' writing.
    pipeline = g.db.pipeline()

    try:
        for entry in json_data:
            cls = _REDIS_LOADER_MAPPING.get(entry['type'], None)
            if cls is not None:
                cls(g.db).save(entry['key'], entry['value'])
    except:
        # Pokemon-catch because this affects all kinds of interruption.
        pipeline.reset()
        raise
    else:
        pipeline.execute()


#: Maps a redis data type to a retrieval function.
_REDIS_FUNC_MAPPING = {
    'set': "smembers",
    'hash': "hgetall",
    'string': "get"
}


def dump_fixture(key):
    """Dumps dict fragment for the given key that is json serializable."""

    type = g.db.type(key)

    try:
        func = _REDIS_FUNC_MAPPING[type]
    except KeyError:
        raise TypeError("Redis keys of type {0} are not yet supported for "
                        "dumping.".format(type))

    value = getattr(g.db, func)(key)

    return {
        'type': type,
        'key': key,
        'value': value}
