# -*- coding: utf-8; Mode: python; tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
# ex: set softtabstop=4 tabstop=4 shiftwidth=4 expandtab fileencoding=utf-8:

# stdlib
import subprocess
import shlex
import logging
import datetime
import os

# python packages
from flask import Flask
from flask import jsonify
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

# flask extensions
# from raven.contrib.flask import Sentry
# from flask_debugtoolbar import DebugToolbarExtension
# from flask.ext.rq import RQ
from api.v1.db import db
from ui import ui


__all__ = ['make_json_app']


def make_json_app(import_name, **kwargs):
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "message": "405: Method Not Allowed" }
    http://flask.pocoo.org/snippets/83/
    """
    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    app = Flask(import_name, **kwargs)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = make_json_app('webhooks', template_folder=tmpl_dir)

# http://flask.pocoo.org/docs/config/
# load base config
app.config.from_object('settings.base')
# $ export RPWEBHOOKS_SETTINGS=/path/to/settings/dev.py
# load additional config
app.config.from_envvar('RPWEBHOOKS_SETTINGS')
# and even add more config
app.config.update(
    PRODUCT_NAME='rpwebhooks',
)


app.url_map.strict_slashes = False
app._logger = logging.getLogger('rpwebhooks')
app.logger_name = 'rpwebhooks'
app.wsgi_app = ProxyFix(app.wsgi_app)
#toolbar = DebugToolbarExtension(app)
#RQ(app)


# http://flask.pocoo.org/docs/blueprints/
from api.v1 import api
app.register_blueprint(api, url_prefix='/api/v1')
app.register_blueprint(ui, url_prefix='/ui')

sentry = Sentry(app, dsn=app.config.get('SENTRY_DNS'))

db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# collect some code and environment info so it can be logged
app.env_attrs = {
    'git_latest_sha': 'git log -n 1 --format=%h',
    'git_branch': 'git rev-parse --abbrev-ref HEAD',
    'git_tag': 'git describe --abbrev=0 --tags',
    'hostname': 'hostname',
}


for app_attr, cmd_str in app.env_attrs.items():
    # split command string with shlex for better os compatibility
    cmd_args = shlex.split(cmd_str)
    # run command
    cmd_proc = subprocess.Popen(cmd_args, stdout=subprocess.PIPE)
    # read result and/or error
    cmd_result, err = cmd_proc.communicate()
    if not err:
        # set an attribute on app with the result
        setattr(app, app_attr, cmd_result.rstrip())


def copyright():
    now = datetime.datetime.now()
    return "&copy; %s %s" % (now.year, app.config['PRODUCT_NAME'])

app.jinja_env.globals['copyright'] = copyright

manager.add_command('runserver', Server(port=app.config.get('SERVER_PORT')))
if __name__ == '__main__':
    if app.debug is not True:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(app.config['LOG_FILE'],
                                           maxBytes=1024 * 1024 * 100,
                                           backupCount=20)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
    manager.run()
