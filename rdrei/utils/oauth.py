# -*- coding: utf-8 -*-
"""
rdrei.utils.oauth
~~~~~~~~~~~~~~~~~

Provides an oauth connector for twitter and possibly other services in the
future.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flaskext.oauth import OAuth
from flask import session
from rdrei import settings

oauth = OAuth()

twitter = oauth.remote_app('twitter',
    base_url='http://api.twitter.com/1/',
    request_token_url='http://api.twitter.com/oauth/request_token',
    access_token_url='http://api.twitter.com/oauth/access_token',
    authorize_url='http://api.twitter.com/oauth/authenticate',
    consumer_key=settings.TWITTER_API_KEY,
    consumer_secret=settings.TWITTER_SECRET_KEY
)

@twitter.tokengetter
def get_twitter_token():
    return session.get('twitter_token')
