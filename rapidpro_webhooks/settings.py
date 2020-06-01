import os

SECRET_KEY = os.environ.get('SECRET_KEY', '8c717393-25ec-4f1c-aedd-96644c6ffb64')
JSON_AS_ASCII = os.environ.get('JSON_AS_ASCII', False)
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI' "postgresql://postgres:@localhost/webhooks")
DEBUG = os.environ.get('DEBUG', False)
PRESERVE_CONTEXT_ON_EXCEPTION = os.environ.get('PRESERVE_CONTEXT_ON_EXCEPTION', False)

GOOGLE_SERVICE_EMAIL = os.environ.get('GOOGLE_SERVICE_EMAIL', 'ft-451@rapidpro-ft.iam.gserviceaccount.com')
RAPIDPRO_EMAIL = os.environ.get('RAPIDPRO_EMAIL', 'rapidprodata@gmail.com')

SERVER_PORT = os.environ.get('SERVER_PORT', 5000)

LOG_FILE = os.getenv('LOG_FILE', '/var/log/webhooks/errors.log')

SENTRY_DSN = os.getenv('SENTRY_DSN')
