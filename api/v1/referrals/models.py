from ..db import db

__author__ = 'kenneth'


class RefCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rapidpro_uuid = db.Column(db.String(100))
    name = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(50))
    group = db.Column(db.String(50))
    country = db.Column(db.String(50))
    created_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    modified_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), server_onupdate=db.func.now())

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

    def get_prefix(self):
        return "%s%s0" % (self.country[:2], self.group)

    @property
    def ref_code(self):
        return "%s%s0%s" % (self.country[:2], self.group, self.id)


class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rapidpro_uuid = db.Column(db.String(50))
    code = db.Column(db.String(50))

    @classmethod
    def is_duplicate(cls, rapidpro_uuid, code):
        dup = cls.query.filter_by(code=code.upper(), rapidpro_uuid=rapidpro_uuid).first()
        if dup:
            return True
        return False

    @classmethod
    def create(cls, rapidpro_uuid, code):
        r = cls(rapidpro_uuid=rapidpro_uuid, code=code)
        db.session.add(r)
        db.session.commit()
        return r