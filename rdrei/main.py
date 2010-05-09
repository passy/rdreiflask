# -*- coding: utf-8 -*-
"""
application
~~~~~~~~~~~

Main entry point for for rdrei.net.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import Flask, render_template, request
app = Flask(__name__)

def _render_template(template_name, **context):
    """Renders a page and supplies the correct extend base."""

    base = "base.html"
    if request.args.get('ajax') is not None:
        base = "base_ajax.html"

    context['template_base'] = base

    return render_template(template_name, **context)


@app.route('/')
def index():
    return _render_template("index.html")

@app.route('/blog')
def blog():
    return _render_template("blog.html")

@app.route('/photos')
def photos():
    return _render_template("photos.html")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
