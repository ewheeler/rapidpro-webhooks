import logging

from sqlalchemy import desc

from rapidpro_webhooks.apps.core.db import db
from rapidpro_webhooks.apps.fusiontables.utils import build_drive_service, build_service
from rapidpro_webhooks.settings import RAPIDPRO_EMAIL


class FT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ft_id = db.Column(db.String(100))


class RefCode(db.Model):
    COLUMNS = ({'name': 'Rapidpro UUID', 'type': 'STRING'}, {'name': 'Join Date', 'type': 'STRING'})
    COLUMN_NAMES = ('Rapidpro UUID', 'Join Date')
    ATTR = ({'name': "ID", "type": "STRING"},
            {'name': "Name", "type": "STRING"}, {'name': "Phone", "type": "STRING"},
            {'name': "Email", "type": "STRING"}, {'name': "Group", "type": "STRING"},
            {'name': "Country", "type": "STRING"}, {'name': "Created On", "type": "STRING"},
            {'name': "Fusion Table ID", "type": "STRING"}, {'name': "Referrals", "type": "STRING"})

    ATTR_NAMES = ("ID", "Name", "Phone", "Email", "Group", "Country", "Created On", "Fusion Table ID", "Referrals")

    id = db.Column(db.Integer, primary_key=True)
    ft_id = db.Column(db.String(100))
    rapidpro_uuid = db.Column(db.String(100))
    name = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(50))
    group = db.Column(db.String(50))
    country = db.Column(db.String(50))
    country_slug = db.Column(db.String(50))
    created_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    modified_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), server_onupdate=db.func.now())
    last_ft_update = db.Column(db.DateTime(timezone=True))
    in_ft = db.Column(db.Boolean, default=False)
    ft_row_id = db.Column(db.String(100))

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
        ref_code.country_slug = country.lower().replace(" ", "_")
        db.session.add(ref_code)
        db.session.commit()
        return ref_code

    @classmethod
    def update_country_slug(cls):
        for obj in cls.query.all():
            obj.country_slug = obj.country.lower().replace(" ", "_")
            db.session.add(obj)
            db.session.commit()

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

    @classmethod
    def get_main_ft_id(cls):
        return FT.query.first().ft_id

    @classmethod
    def create_main_ft(cls):
        service = build_service()
        table = {'name': "Ureport Referrals", 'description': "Code and the number of referrals per code",
                 'isExportable': True, 'columns': cls.ATTR}
        table = service.table().insert(body=table).execute()
        service = build_drive_service()
        body = {'role': 'writer', 'type': 'user', 'emailAddress': RAPIDPRO_EMAIL, 'value': RAPIDPRO_EMAIL}
        service.permissions().insert(fileId=table.get('tableId'), body=body, sendNotificationEmails=True).execute()
        db.session.add(FT(ft_id=table.get('tableId')))
        db.session.commit()
        return table

    @classmethod
    def update_main_ft(cls):
        service = build_service()
        for code in cls.query.all():
            if code.in_ft:
                sql = "UPDATE %s SET Referrals = %d WHERE ROWID = '%s'" % (cls.get_main_ft_id(),
                                                                           code.get_referral_count(), code.ft_row_id)
                service.query().sql(sql=sql).execute()
            else:
                values = (str(code.id), str(code.name).replace("'", "\\'"), str(code.phone), str(code.email),
                          str(code.group).replace("'", "\\'"), str(code.country).replace("'", "\\'"),
                          str(code.created_on), str(code.ft_id), str(code.get_referral_count()))
                sql = 'INSERT INTO %s %s VALUES %s' % (cls.get_main_ft_id(), str(cls.ATTR_NAMES), str(values))
                response = service.query().sql(sql=sql).execute()
                code.in_ft = True
                code.ft_row_id = response['rows'][0][0]
                db.session.add(code)
                db.session.commit()

            logging.info(sql)

    def get_prefix(self):
        return "%s%s0" % (self.country[:2], self.group)

    @property
    def ref_code(self):
        code = "%s%s0%s" % (self.country[:2], self.group, self.id)
        return code.upper()

    def get_referrals(self, last_update=False):
        if last_update:
            return Referral.query.filter(Referral.ref_code == self.id).\
                filter(Referral.created_on >= self.last_ft_update).order_by(desc(Referral.created_on))
        return Referral.query.filter_by(ref_code=self.id).order_by(desc(Referral.created_on))

    def get_referral_count(self):
        return self.get_referrals().count()

    @property
    def ref_count(self):
        return self.get_referral_count()

    def create_ft(self):
        service = build_service()
        table = {'name': self.name, 'description': "Referrals for Code %s" % self.id, 'isExportable': True,
                 'columns': self.COLUMNS}
        table = service.table().insert(body=table).execute()
        self.ft_id = table.get('tableId')
        self.give_rapidpro_permission()
        self.give_rapidpro_permission(RAPIDPRO_EMAIL)
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

    def give_rapidpro_permission(self, email=None):
        if not email:
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
