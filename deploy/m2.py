# -*- coding: utf-8 -*-
"""
Run the application with a zmq/mongrel2 backend. Based on
``http://github.com/berry/Mongrel2-WSGI-Handler/``_.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: BSD
"""

from __future__ import unicode_literals, absolute_import
import os
import sys
from mongrel2 import handler
from mongrel2_wsgi import wsgi_server


if __name__ == '__main__':
    sys.path.append(os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir)))

    from rdrei.application import app
    wsgi_server(app,
                handler.Connection(
                    b"a97fde5c-6915-4644-bb43-90e774f2e1bb", 
                    b"tcp://127.0.0.1:9997",
                    b"tcp://127.0.0.1:9996"
                ))
