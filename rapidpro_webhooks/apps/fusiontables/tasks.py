from celery import Celery
from flask_migrate import Migrate

from rapidpro_webhooks import settings
from rapidpro_webhooks.app import make_json_app
from rapidpro_webhooks.apps.core.db import db
from rapidpro_webhooks.apps.fusiontables.models import Flow

app = make_json_app('webhooks')

# http://flask.pocoo.org/docs/config/
# load base config

app.config.from_object(settings)
# $ export RPWEBHOOKS_SETTINGS=/path/to/settings/dev.py
# load additional config
# app.config.from_envvar('RPWEBHOOKS_SETTINGS')
# and even add more config
app.config.update(
    PRODUCT_NAME='rpwebhooks',
)

# Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery("webhooks", broker=app.config['CELERY_BROKER_URL'])

db.init_app(app)
migrate = Migrate(app, db)
app.app_context().push()


@celery.task
def update_fusion_table(flow_id, phone, values, email, base_language):
    flow = Flow.query.get(flow_id)
    flow.update_email(email)
    flow.update_fusion_table(phone, values, base_language)


@celery.task
def create_flow_and_update_ft(data, email, phone, values, base_language):
    flow = Flow.create_from_run(data, email)
    flow.update_fusion_table(phone, values, base_language)
