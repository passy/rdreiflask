# -*- coding: utf-8 -*-
"""
rdrei.views.base
~~~~~~~~~~~~~~~~

Basic views.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from __future__ import unicode_literals, print_function, absolute_import
from flask import g, session, request, flash, redirect, url_for, Module
from rdrei.utils.oauth import twitter
from rdrei.utils.template import render_template


base = Module(__name__)


@base.route('/')
def home():
    return render_template("index.html")


@base.route('/blog')
def blog_index():
    return render_template("blog.html")


@base.route('/about')
def about():
    return render_template("about.html")


@base.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(response):
    next_url = request.args.get('next') or url_for('home')
    if response is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['twitter_token'] = (
        response['oauth_token'],
        response['oauth_token_secret'])
    session['twitter_user'] = response['screen_name']

    flash('You were signed in as %s' % response['screen_name'])
    return redirect(next_url)
