# -*- coding: utf-8 -*-
"""
rdrei.views.admin
~~~~~~~~~~~~~~~~~

Admin views.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import url_for, request, redirect, flash, Module
from rdrei.application import app
from rdrei.models import PhotoAlbums
from rdrei.utils.oauth import twitter
from rdrei.utils.auth import requires_admin
from rdrei.utils.template import templated, render_template
from rdrei.forms import PhotoAlbumForm
from werkzeug.exceptions import NotFound


admin = Module(__name__, url_prefix="/admin")


@admin.route('/login')
def login():
    next = request.args.get('next') or request.referrer or None
    return twitter.authorize(
        callback=url_for('.oauth_authorized', next=next))


@admin.route('/photos', methods=['GET', 'POST'])
@admin.route('/photos/<int:album_id>/', methods=['GET', 'POST'])
@requires_admin
def photo(album_id=None):
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
            if album is None:
                flash("New album created.")
            else:
                flash("Album saved.")
            return redirect(url_for("photos.index"))
    else:
        form = PhotoAlbumForm(obj=album)

    return render_template('admin/photos.html',
        form=form,
        album_id=album_id)
