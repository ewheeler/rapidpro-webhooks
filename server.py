# -*- coding: utf-8; Mode: python; tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
# ex: set softtabstop=4 tabstop=4 shiftwidth=4 expandtab fileencoding=utf-8:

# stdlib
import subprocess
import shlex
import logging
import datetime

# python packages
from flask import Flask
from flask import jsonify
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

# flask extensions
# from raven.contrib.flask import Sentry
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.rq import RQ


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

app = make_json_app('rolodex')

# http://flask.pocoo.org/docs/config/
app.config.from_object('settings.base')
app.config.update(
    DEBUG=True,
)
#app.config.from_object('config')
app.url_map.strict_slashes = False
app._logger = logging.getLogger('rolodex')
app.logger_name = 'rolodex'
app.wsgi_app = ProxyFix(app.wsgi_app)
toolbar = DebugToolbarExtension(app)
RQ(app)


# http://flask.pocoo.org/docs/blueprints/
from api.v1 import api
app.register_blueprint(api, url_prefix='/api/v1')

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


def is_printable(s):
    """ jinja2 test to determine whether a string can be printed
        by a template without error.
    """
    try:
        s.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False
    except UnicodeEncodeError:
        return False
    except AttributeError:
        return True

app.jinja_env.tests['printable'] = is_printable


def copyright():
    now = datetime.datetime.now()
    #return "&copy; %s %s" % (now.year, app.config['BRAND_DOMAIN'])
    return "&copy; %s %s" % (now.year, 'ureport')

app.jinja_env.globals['copyright'] = copyright

if __name__ == '__main__':
    app.run(port=5050)
