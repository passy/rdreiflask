#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
"""
rdreiflask.manage
~~~~~~~~~~~~~~~~~

Management script.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from werkzeug import script
from rdrei.models import Photos


def action_runserver():
    from rdrei.application import app

    app.run(debug=True, host="0.0.0.0")


if __name__ == '__main__':
    script.run()
# vim: set ts=8 sw=4 tw=78 ft=python: 
