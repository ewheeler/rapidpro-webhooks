import random
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

from stdnum import verhoeff

from ..exceptions import VoucherException
db = SQLAlchemy()

__author__ = 'kenneth'


class Voucher(db.Model):
    __tablename__ = 'voucher_vouchers'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6))
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
    def redeem(cls, code, phone):
        voucher = cls.query.filter_by(code=str(code), redeemed_on=None).first()
        if voucher is None:
            raise VoucherException("Attempting to redeem an already redeemed voucher")
        voucher.redeemed_on = datetime.now()
        voucher.redeemed_by = phone
        db.session.add(voucher)
        db.session.commit()

    @classmethod
    def _random(cls):
        _code = random.randint(10000, 99999)
        while cls.query.filter_by(code=str(_code)).first():
            _code = random.randint(10000, 99999)
        return _code

    @classmethod
    def generate_code(cls):
        _code = cls._random()
        check_digit = verhoeff.calc_check_digit(_code)
        return "%s%s" % (str(_code), str(check_digit))