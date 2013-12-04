import datetime

from .base import ContactBaseResource
from .base import ResourceError


class ValidationError(ResourceError):

    def __init__(self, field, message):
        self.field = field
        self.message = message


class ContactResource(ContactBaseResource):

    def get(self, id=None):
        contact = [{'name': 'evan',
                    'identities': [{'backend': 'mtn',
                                    'backend_type': 'gsm',
                                    'id': '1234'}],
                    'signup_product': 'ureport',
                    'last_seen': {'product': 'ureport',
                                  'datetime': datetime.datetime.utcnow()
                                  .isoformat()},
                    'products': ['ureport', 'mtrac'],
                    'location': 'kampala'}]
        return contact
