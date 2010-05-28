#!/usr/bin/env python

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import sys
import os


sys.path.append(os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir)))


from rdrei.application import app


http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5000)
IOLoop.instance().start()
