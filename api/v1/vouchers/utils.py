from googleapiclient.discovery import build
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from settings.base import GOOGLE_SERVICE_EMAIL

__author__ = 'kenneth'


def do_auth():
    credentials = ServiceAccountCredentials.from_p12_keyfile(GOOGLE_SERVICE_EMAIL, 'auth/fusiontable.p12',
                                                             scopes=['https://www.googleapis.com/auth/fusiontables',
                                                                     'https://www.googleapis.com/auth/drive'])
    http = httplib2.Http()
    auth = credentials.authorize(http)
    if credentials.access_token_expired: auth.login()
    return auth


def build_service():
    return build('fusiontables', 'v2', http=do_auth())

def build_drive_service():
    return build('drive', 'v2', http=do_auth())