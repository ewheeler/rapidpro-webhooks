# -*- coding: utf-8; Mode: python; tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
# ex: set softtabstop=4 tabstop=4 shiftwidth=4 expandtab fileencoding=utf-8:

import datetime
import logging
import os
import shlex
# stdlib
import subprocess

# python packages
from celery import Celery
from flask_admin import Admin
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server
from werkzeug.middleware.proxy_fix import ProxyFix

# http://flask.pocoo.org/docs/config/
# load base config
from rapidpro_webhooks import settings
# http://flask.pocoo.org/docs/blueprints/
from rapidpro_webhooks.api import api
# flask extensions
# from raven.contrib.flask import Sentry
# from flask_debugtoolbar import DebugToolbarExtension
# from flask_rq import RQ
from rapidpro_webhooks.api.db import db
from rapidpro_webhooks.api.referrals.admin import ReferralModelView, RefModelView, UserModelView
from rapidpro_webhooks.api.referrals.models import RefCode, Referral, User
from rapidpro_webhooks.app import make_json_app
from rapidpro_webhooks.ui import ui

from .manage import CreateFT, CreateMainFT, CreateSuperUser, UpdateCountrySlug, UpdateFt, UpdateMainFT

__all__ = ['make_json_app']

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = make_json_app('webhooks', template_folder=tmpl_dir)

app.config.from_object(settings)
# load additional config
# app.config.from_envvar('RPWEBHOOKS_SETTINGS')
# and even add more config
app.config.update(
    PRODUCT_NAME='rpwebhooks',
)


app.url_map.strict_slashes = False
app._logger = logging.getLogger('rpwebhooks')
app.logger_name = 'rpwebhooks'
app.wsgi_app = ProxyFix(app.wsgi_app)
# toolbar = DebugToolbarExtension(app)
# RQ(app)


app.register_blueprint(api, url_prefix='/api/v1')
app.register_blueprint(ui, url_prefix='/ui')

if app.debug is not True:
    from raven.contrib.flask import Sentry
    sentry = Sentry(app, dsn=app.config.get('SENTRY_DSN'))

db.init_app(app)
migrate = Migrate(app, db)

# Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery("webhooks", broker=app.config['CELERY_BROKER_URL'])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


admin = Admin(app, name="Referrals", template_mode='bootstrap3')
admin.add_view(RefModelView(RefCode, db.session, name="Partners"))
admin.add_view(ReferralModelView(Referral, db.session, name="Referrals"))
admin.add_view(UserModelView(User, db.session, name="Users"))

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('updateft', UpdateFt())
manager.add_command('createft', CreateFT())
manager.add_command('createmainft', CreateMainFT())
manager.add_command('updatemainft', UpdateMainFT())
manager.add_command('updatecountryslug', UpdateCountrySlug())
manager.add_command('createsuperuser', CreateSuperUser())

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
