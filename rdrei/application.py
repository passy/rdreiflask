# -*- coding: utf-8 -*-
"""
application
~~~~~~~~~~~

Main entry point for for rdrei.net.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from flask import Flask
app = Flask(__name__)


import rdrei.views
