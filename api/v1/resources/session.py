import uuid
import datetime

from .base import BaseResource


class SessionResource(BaseResource):

    def __init__(self):
        # TODO real storage
        self.sessions = {}

    def create(self, identity, source, product):
        sid = uuid.uuid4().hex
        payload = {'id': sid,
                   'identity': identity,
                   'source': source,
                   'product': product,  # e.g., ureport, mtrac, edutrac
                   'created': datetime.datetime.utcnow().isoformat(),
                   'updated': datetime.datetime.utcnow().isoformat()}
        self.sessions.update({sid: payload})
        return payload

    def get(self, id):
        session = self.sessions.get(id)
        return session

    def update(self, id, data):
        session = self.sessions.get(id)
        session.update(data)
        session.update({'updated': datetime.datetime.utcnow().isoformat()})
        self.sessions.update({id: session})
        return session
