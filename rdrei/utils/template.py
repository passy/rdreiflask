# -*- coding: utf-8 -*-
"""
rdrei.utils.template
~~~~~~~~~~~~~~~~~~~~

Template rendering helpers.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import render_template as _render_template, request
from functools import wraps


def render_template(template_name, **context):
    """Renders a page and supplies the correct extend base."""

    base = "base.html"
    if request.args.get('ajax') is not None:
        base = "base_ajax.html"

    context['template_base'] = base

    return _render_template(template_name, **context)


def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator
