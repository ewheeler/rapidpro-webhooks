from sqlalchemy import desc

from rapidpro_webhooks.apps.core.db import db


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
