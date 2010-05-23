# -*- coding: utf-8 -*-
"""
rdrei.views
~~~~~~~~~~~

Routing and outputting the views.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import g, session, request, flash, redirect
from rdrei.utils.oauth import twitter
from rdrei.application import app
from rdrei.utils.template import render_template


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/blog')
def blog_index():
    return render_template("blog.html")


@app.route('/oauth-authorized')
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
