# -*- coding: utf-8 -*-
"""
rdrei.views
~~~~~~~~~~~

Routing and outputting the views.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from rdrei.application import app
from rdrei.utils.template import render_template


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/blog')
def blog():
    return render_template("blog.html")


@app.route('/photos')
def photos():
    return render_template("photos.html")
