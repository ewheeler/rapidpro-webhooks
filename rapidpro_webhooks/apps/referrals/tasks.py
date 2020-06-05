from flask_migrate import Migrate

from rapidpro_webhooks.app import make_json_app
from rapidpro_webhooks.apps.core.db import db

app = make_json_app('webhooks')

# http://flask.pocoo.org/docs/config/
# load base config
app.config.from_object('settings')
# $ export RPWEBHOOKS_SETTINGS=/path/to/settings/dev.py
# load additional config
app.config.from_envvar('RPWEBHOOKS_SETTINGS')
# and even add more config
app.config.update(
    PRODUCT_NAME='rpwebhooks',
)

db.init_app(app)
migrate = Migrate(app, db)
app.app_context().push()
