from rapidpro_webhooks import settings
from rapidpro_webhooks.app import make_json_app

from .views import *  # noqa

app = make_json_app('webhooks')
app.config.from_object(settings)

app.app_context().push()
