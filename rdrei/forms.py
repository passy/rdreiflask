# -*- coding: utf-8 -*-
"""
forms
~~~~~

WTForm definitions.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from rdrei.models import PhotoAlbum
from wtforms import Form, TextField, TextAreaField, IntegerField, validators


class PhotoAlbumForm(Form):
    """Form to add or edit a photo album."""

    title = TextField("Title", [validators.Length(min=4, max=100)])
    tag = TextField("Album Tag", [validators.Length(min=4, max=50)])
    description = TextAreaField("Description")
    frontcover = IntegerField("Front Cover ID")

    def save(self, instance=None):
        """
        Saves the entry and does an insert or an update, based on
        ``instance``.
        """

        if instance:
            self.populate_obj(instance)
        else:
            instance = PhotoAlbum({
                'title': self.title.data,
                'tag': self.tag.data,
                'description': self.description.data,
                'frontcover': self.frontcover.id})

        instance.save()
