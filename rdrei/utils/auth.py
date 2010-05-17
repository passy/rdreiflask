# -*- coding: utf-8 -*-
"""
rdrei.utils.auth
~~~~~~~~~~~~~~~~

Authentication utils.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from functools import wraps
from flask import request, g, redirect, home, flash


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.authorized:
            return f(*args, **kwargs)

        flash("Du hast keine Berechtigung für diese Seite. Sorry!")
        return redirect(url_for("home"))
    return decorated
