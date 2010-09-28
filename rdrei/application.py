# -*- coding: utf-8 -*-
"""
application
~~~~~~~~~~~

Main entry point for for rdrei.net.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import Flask, g, session
from rdrei import settings, __version__

from rdrei.utils import redis
from rdrei.views.photos import photos
from rdrei.views.admin import admin
from rdrei.views.base import base


def create_app(config=None):
    """Creates a new application object."""

    app = Flask("rdrei")
    app.config.from_object(settings)
    app.config.from_envvar("RDREI_SETTINGS", silent=True)
    app.register_module(photos)
    app.register_module(admin)
    app.register_module(base)

    @app.context_processor
    def _set_template_vars():
        """Make debug mode and version available to the template."""
        return dict(VERSION=__version__)

    @app.before_request
    def _open_redis():
        g.db = redis.open_connection(app.config.get('REDIS_HOST'),
                                    app.config.get('REDIS_PORT'),
                                    app.config.get('REDIS_DATABASE'))

    @app.before_request
    def _check_login():
        """Sets g.logged_in to true if the user is logged in via 
        twitter and matches a user name defined in
        ``settings.ADMIN_USERS``.
        """

        if session.get('twitter_user', None) in app.config['ADMIN_USERS']:
            g.is_admin = True
        else:
            g.is_admin = False

    return app
