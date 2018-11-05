import os
from flask import Flask

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


__all__ = [
    'HttpServer'
]


class HttpServer(object):

    def __init__(self, name, http_port):
        self.app = Flask(name)
        self.port = http_port
        self.server = None

    def start(self):
        from .controllers import admin, workflow
        app, port = self.app, self.port

        app.register_blueprint(admin)
        app.register_blueprint(workflow)

        for rule in app.url_map.iter_rules():
            print(rule)
        app.secret_key = os.urandom(1)

        self._launch_tornado(app, port)

    def stop(self):
        self.server.stop()

    def _launch_tornado(self, app, port):
        self.server = HTTPServer(WSGIContainer(app))
        self.server.listen(port)
        IOLoop.instance().start()
