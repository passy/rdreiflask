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
from rdrei.models import PhotoAlbums
from rdrei.utils.oauth import twitter
from rdrei.utils.auth import requires_admin
from rdrei.utils.template import templated, render_template
from rdrei.forms import PhotoAlbumForm
from werkzeug.exceptions import NotFound


@app.route('/admin/login')
def admin_login():
    next = request.args.get('next') or request.referrer or None
    return twitter.authorize(
        callback=url_for('oauth_authorized', next=next)
    )


@app.route('/admin/photos', methods=['GET', 'POST'])
@app.route('/admin/photos/<int:album_id>/', methods=['GET', 'POST'])
@requires_admin
def admin_photo(album_id=None):
    """
    Displays a form to either add or edit a photo album. If the album is
    created from scratch or updates an existing depends on the presence of the
    ``album_id`` parameter.
    """

    album = None
    if album_id is not None:
        album = PhotoAlbums.by_id(album_id)
        if album is None:
            raise NotFound("Photo album not found.")

    if request.method == "POST":
        form = PhotoAlbumForm(request.form, obj=album)
        if form.validate():
            form.save(album)
            return redirect(url_for("photo_index"))
    else:
        form = PhotoAlbumForm(obj=album)

    return render_template('admin/photos.html',
        form=form,
        album_id=album_id
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
