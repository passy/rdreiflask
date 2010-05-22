# -*- coding: utf-8 -*-
"""
rdrei.utils.auth
~~~~~~~~~~~~~~~~

Authentication utils.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from functools import wraps
from flask import request, g, redirect, flash, url_for


def requires_admin(f):
    """Decorator for views that require admin privileges."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.is_admin:
            return f(*args, **kwargs)

        # TODO: i18n
        flash("Nothing to see here. Move along!")
        return redirect(url_for("home"))
    return decorated
