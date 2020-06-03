import random
from datetime import datetime

from stdnum import verhoeff

from rapidpro_webhooks.apps.core.db import db
from rapidpro_webhooks.apps.core.exceptions import VoucherException


class Voucher(db.Model):
    __tablename__ = 'voucher_vouchers'

    id = db.Column(db.Integer, primary_key=True)
    flow_id = db.Column(db.Integer, nullable=True)
    code = db.Column(db.String(20))
    redeemed_on = db.Column(db.DateTime(timezone=True), nullable=True)
    created_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    modified_on = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), server_onupdate=db.func.now())
    redeemed_by = db.Column(db.String(13), nullable=True)

    def __init__(self, code):
        self.code = code

    def __repr__(self):
        return self.code

    @classmethod
    def create(cls):
        voucher = cls(code=cls.generate_code())
        db.session.add(voucher)
        db.session.commit()
        return voucher

    @classmethod
    def add_external_codes(cls, codes):
        codes = set(codes)
        for code in codes:
            voucher = cls(code=code)
            db.session.add(voucher)
        db.session.commit()

    @classmethod
    def redeem(cls, code, phone, flow):
        voucher = cls.query.filter_by(code=str(code)).first()
        if voucher is None:
            raise VoucherException("Voucher does not exist")
        if voucher.redeemed_on is not None:
            raise VoucherException("Attempting to redeem an already redeemed voucher")
        voucher.redeemed_on = datetime.now()
        voucher.redeemed_by = phone
        voucher.flow_id = flow
        db.session.add(voucher)
        db.session.commit()

    @classmethod
    def _random(cls):
        _code = random.randint(100, 999)
        while cls.query.filter_by(code=str(_code)).first():
            _code = random.randint(100, 999)
        return _code

    @classmethod
    def generate_code(cls):
        _code = cls._random()
        check_digit = verhoeff.calc_check_digit(_code)
        return "%s%s" % (str(_code), str(check_digit))
