import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from rapidpro_webhooks.settings import GOOGLE_SERVICE_EMAIL


def do_auth():
    credentials = ServiceAccountCredentials.from_p12_keyfile(GOOGLE_SERVICE_EMAIL, 'auth/fusiontable.p12',
                                                             scopes=['https://www.googleapis.com/auth/fusiontables',
                                                                     'https://www.googleapis.com/auth/drive'])
    http = httplib2.Http()
    auth = credentials.authorize(http)
    if credentials.access_token_expired:
        auth.login()
    return auth


def build_service():
    return build('fusiontables', 'v2', http=do_auth())


def build_drive_service():
    return build('drive', 'v2', http=do_auth())
