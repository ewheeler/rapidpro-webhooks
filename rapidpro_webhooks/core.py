import datetime
import logging
import os
import shlex
import subprocess
from logging.handlers import RotatingFileHandler

import sentry_sdk
from flask_admin import Admin
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

from rapidpro_webhooks import settings
from rapidpro_webhooks.app import make_json_app
from rapidpro_webhooks.apps import core, eum, mvrs, places, referrals, thousand, ureport, vouchers
from rapidpro_webhooks.apps.core import User
from rapidpro_webhooks.apps.core.admin import UserModelView
from rapidpro_webhooks.apps.core.db import db
from rapidpro_webhooks.apps.referrals.admin import ReferralModelView, RefModelView
from rapidpro_webhooks.apps.referrals.models import RefCode, Referral
from rapidpro_webhooks.apps.vouchers import Voucher
from rapidpro_webhooks.apps.vouchers.admin import VoucherView
from rapidpro_webhooks.ui import ui

logging.basicConfig(level=logging.WARNING)

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = make_json_app('webhooks', template_folder=tmpl_dir)


app.config.from_object(settings)
app.app_context().push()
app_name = app.config.get('APP_NAME')
app.config.update(PRODUCT_NAME='rpwebhooks')

log_file = app.config['LOG_FILE']
file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)


app.url_map.strict_slashes = False
app._logger = logging.getLogger('rpwebhooks')
app.logger_name = 'rpwebhooks'
app.wsgi_app = ProxyFix(app.wsgi_app)


app.register_blueprint(core.core_bp, url_prefix='/')
app.register_blueprint(eum.eum_bp, url_prefix='/api/v1/eum/')
app.register_blueprint(mvrs.mvrs_bp, url_prefix='/api/v1/mvrs/')
app.register_blueprint(places.places_bp, url_prefix='/api/v1/')
app.register_blueprint(referrals.referrals_bp, url_prefix='/api/v1/referral')
app.register_blueprint(thousand.thousand_bp, url_prefix='/api/v1/thousand/')
app.register_blueprint(ureport.ureport_bp, url_prefix='/api/v1/ureport/')
app.register_blueprint(vouchers.voucher_bp, url_prefix='/api/v1/voucher/')
app.register_blueprint(ui.ui_bp, url_prefix='/ui')

if app.debug is not True and app.config['SENTRY_DSN']:
    sentry_sdk.init(dsn=app.config['SENTRY_DSN'])

db.init_app(app)
MIGRATION_DIR = os.path.join('rapidpro_webhooks', 'migrations')
migrate = Migrate(app, db, directory=MIGRATION_DIR)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


admin = Admin(app, name="Admin", template_mode='bootstrap3')
admin.add_view(UserModelView(User, db.session, name="Users"))
admin.add_view(RefModelView(RefCode, db.session, name="Partners"))
admin.add_view(ReferralModelView(Referral, db.session, name="Referrals"))
admin.add_view(VoucherView(Voucher, db.session, name="Vouchers", endpoint="vouchers"))

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
