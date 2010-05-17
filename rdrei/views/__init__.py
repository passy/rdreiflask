# -*- coding: utf-8 -*-
"""
rdrei.views
~~~~~~~~~~~

Routing and outputting the views.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import g
from rdrei.application import app
from rdrei.utils.template import render_template


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/blog')
def blog_index():
    return render_template("blog.html")


import rdrei.views.photos
import rdrei.views.admin
