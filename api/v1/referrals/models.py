import logging
from sqlalchemy import desc
from api.v1.fusiontables.utils import build_service, build_drive_service
from ..db import db
from settings.base import RAPIDPRO_EMAIL

__author__ = 'kenneth'


class RefCode(db.Model):
    COLUMNS = ({'name': 'Rapidpro UUID', 'type': 'STRING'}, {'name': 'Join Date', 'type': 'STRING'})
    COLUMN_NAMES = ('Rapidpro UUID', 'Join Date')

    id = db.Column(db.Integer, primary_key=True)
    ft_id = db.Column(db.String(100))
    rapidpro_uuid = db.Column(db.String(100))
    name = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(50))
    group = db.Column(db.String(50))
    country = db.Column(db.String(50))
    created_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    modified_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), server_onupdate=db.func.now())
    last_ft_update = db.Column(db.DateTime(timezone=True))

    @classmethod
    def create_code(cls, rapidpro_uuid, name, phone, email, group, country):
        c = cls.get_by_uuid(rapidpro_uuid)
        if c:
            return c
        ref_code = cls(rapidpro_uuid=rapidpro_uuid)
        ref_code.name = name
        ref_code.phone = phone
        ref_code.email = email
        ref_code.group = group
        ref_code.country = country
        db.session.add(ref_code)
        db.session.commit()
        return ref_code

    @classmethod
    def get_by_code(cls, code):
        _id = code.split('0', 1)
        if len(_id) < 2:
            return None
        return cls.query.filter_by(id=int(_id[1])).first()

    @classmethod
    def get_by_uuid(cls, uuid):
        return cls.query.filter_by(rapidpro_uuid=uuid).first()

    @classmethod
    def get_with_no_ft_id(cls):
        return cls.query.filter_by(ft_id=None)

    def get_prefix(self):
        return "%s%s0" % (self.country[:2], self.group)

    @property
    def ref_code(self):
        return "%s%s0%s" % (self.country[:2], self.group, self.id)

    def get_referrals(self, last_update=False):
        if last_update:
            return Referral.query.filter(Referral.ref_code == self.id).\
                filter(Referral.created_on >= self.last_ft_update).order_by(desc(Referral.created_on))
        return Referral.query.filter_by(ref_code=self.id).order_by(desc(Referral.created_on))

    def create_ft(self):
        service = build_service()
        table = {'name': self.name, 'description': "Referrals for Code %s" % self.id, 'isExportable': True,
                 'columns': self.COLUMNS}
        table = service.table().insert(body=table).execute()
        self.ft_id = table.get('tableId')
        self.give_rapidpro_permission()
        db.session.add(self)
        db.session.commit()
        return table

    def update_fusion_table(self):
        service = build_service()
        refs = self.get_referrals(True) if self.last_ft_update else self.get_referrals()
        values = [str((str(ref.rapidpro_uuid), str(ref.created_on))) for ref in refs]
        v = [(ref.rapidpro_uuid, str(ref.created_on)) for ref in refs]
        if values:
            self.last_ft_update = v[0][1]
            sql = 'INSERT INTO %s %s VALUES %s' % (self.ft_id, str(self.COLUMN_NAMES), ','.join(values))
            logging.info(sql)
            update = service.query().sql(sql=sql).execute()
            db.session.add(self)
            db.session.commit()
            return update

    def give_rapidpro_permission(self):
        email = self.email or RAPIDPRO_EMAIL
        service = build_drive_service()
        body = {'role': 'writer', 'type': 'user', 'emailAddress': email, 'value': email}
        return service.permissions().insert(fileId=self.ft_id, body=body, sendNotificationEmails=True).execute()


class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rapidpro_uuid = db.Column(db.String(50))
    code = db.Column(db.String(50))
    ref_code = db.Column(db.Integer)
    created_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    @classmethod
    def is_duplicate(cls, rapidpro_uuid, code):
        dup = cls.query.filter_by(code=code.upper(), rapidpro_uuid=rapidpro_uuid).first()
        if dup:
            return True
        return False

    @classmethod
    def create(cls, rapidpro_uuid, code):
        r = cls(rapidpro_uuid=rapidpro_uuid, code=code, ref_code=RefCode.get_by_code(code).id)
        db.session.add(r)
        db.session.commit()
        return r