# -*- coding: utf-8 -*-
"""
rdrei.views.admin
~~~~~~~~~~~~~~~~~

Admin views.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import url_for, request, redirect, flash, Module, g
from rdrei.application import app
from rdrei.models import PhotoAlbums, Photos
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


@admin.route('/album', methods=['GET', 'POST'])
@admin.route('/album/<int:album_id>', methods=['GET', 'POST'])
@requires_admin
def edit_album(album_id=None):
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


@admin.route('/album_delete/<int:album_id>')
@requires_admin
def delete_album(album_id=None):
    """
    Deletes a complete album. But only the association, not the photos
    themselves.
    """

    # We could use a method of PhotoAlbum, but as this is an admin function,
    # it's quite unimportant if the album actually exists. This is the
    # cheapest call we can make.
    g.db.delete("photoalbum:" + str(album_id))
    flash("Album deleted.")
    return redirect(url_for("photos.index"))


@admin.route('/photo/toggle_orientation/<int:photo_id>')
@requires_admin
def photo_toggle_orientation(photo_id):
    """
    Toggles the vertical/horizontal orientation of a photo.
    """

    photo = Photos.by_id(photo_id)
    photo.horizontal = int(photo.horizontal == False)
    photo.save()
    return photo.horizontal and 'horizontal' or 'vertical'
