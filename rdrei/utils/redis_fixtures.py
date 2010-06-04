# -*- coding: utf-8 -*-
"""
redis_fixtures
~~~~~~~~~~~~~~

Loading data into redis from JSOM files.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: BSD
"""

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
    'list': RedisListLoader}


def load_fixture(redis_db, filename):
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

    :param redis_db: A pyredis instance.
    :param filename: Path to the fixture json file.
    """

    json_data = simplejson.load(open(filename, 'r'))
    # Create a new pipeline for 'transactional' writing.
    pipeline = redis_db.pipeline()

    try:
        for entry in json_data:
            cls = _REDIS_LOADER_MAPPING.get(entry['type'], None)
            if cls is not None:
                cls(redis_db).save(entry['key'], entry['value'])
    except:
        # Pokemon-catch because this affects all kinds of interruption.
        pipeline.reset()
        raise
    else:
        pipeline.execute()
