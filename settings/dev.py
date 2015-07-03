from settings.base import *
DEBUG=True
SERVER_PORT = 8009
LOG_FILE = '/var/log/webhooks/test_errors.log'
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:@localhost/test_webhooks"
