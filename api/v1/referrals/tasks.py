from celery import Celery
from flask.ext.migrate import Migrate
from api.v1.db import db
from app import make_json_app

__author__ = 'kenneth'
app = make_json_app('webhooks')

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

#Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery("webhooks", broker=app.config['CELERY_BROKER_URL'])

db.init_app(app)
migrate = Migrate(app, db)
app.app_context().push()

@celery.task
def update_referral_ft(_id):
    pass


@celery.task
def create_referral_ft(_id):
    pass