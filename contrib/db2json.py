# -*- coding: utf-8 -*-
"""
db2json
~~~~~~~

Converts my old sqlite db to a json fixture.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

import sqlite3
from python import json
from contextlib import closing


def connect_db():
    return sqlite3.connect("database.sqlite")


def get_photos(db):
    cursor = db.execute("SELECT title, flickr_id, flickr_server, "
                        "flickr_secret, flickr_tags FROM photos_photo")
    for entry in cursor.fetchall():
        # The order that is usually in redis.
        yield {
            'title': entry[0],
            'farm': 4,
            'server': entry[2],
            'secret': entry[3],
            'id': entry[1],
            '_tags': entry[4]}


def main():
    result = []
    with closing(connect_db()) as db:
        for entry in get_photos(db):
            key = "photo:" + str(entry['id'])
            tags = entry['_tags']
            del entry['_tags']

            result.append({
                'type': "hash",
                'key': key,
                'value': entry})

            result.append({
                'type': "set",
                'key': "photos",
                'value': entry['id']})

            for tag in tags.split(' '):
                # Make sure it's not an empty string.
                if tag:
                    key = "phototags:" + tag
                else:
                    key = "phototags:untagged"

                result.append({
                    'type': "set",
                    'key': key,
                    'value': entry['id']
                })

    print(json.dumps(result))


if __name__ == '__main__':
    main()
