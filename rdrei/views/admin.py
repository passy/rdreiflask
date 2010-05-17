# -*- coding: utf-8 -*-
"""
rdrei.views.admin
~~~~~~~~~~~~~~~~~

Admin views.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import url_for, request, redirect, session, flash
from rdrei.application import app
from rdrei.utils.oauth import twitter


@app.route('/admin/login')
def admin_login():
    next = request.args.get('next') or request.referrer or None
    return twitter.authorize(
        callback=url_for('oauth_authorized', next=next)
    )


@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(response):
    next_url = request.args.get('next') or url_for('home')
    if response is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['twitter_token'] = (
        response['oauth_token'],
        response['oauth_token_secret']
    )
    session['twitter_user'] = response['screen_name']

    flash('You were signed in as %s' % response['screen_name'])
    return redirect(next_url)
