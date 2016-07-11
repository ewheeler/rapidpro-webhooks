import json
import random
from datetime import datetime

from stdnum import verhoeff
from settings.base import RAPIDPRO_EMAIL
from utils import build_service, build_drive_service
from ..db import db

from ..exceptions import VoucherException

__author__ = 'kenneth'


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


class Flow(db.Model):
    __tablename__ = 'fusion_table_flows'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    flow_id = db.Column(db.Integer)
    name = db.Column(db.String)
    ft_id = db.Column(db.String)
    ft_columns = db.Column(db.String)
    email = db.Column(db.String, nullable=True)

    @classmethod
    def create_from_run(cls, run, email):
        flow_id = run.get('flow')

        values = json.loads(run.get('values'))
        columns = cls.get_columns_from_values(values)

        flow = cls.create(flow_id, flow_id, columns, email)
        return flow


    @classmethod
    def get_by_flow(cls, flow_id):
        return cls.query.filter_by(flow_id=int(flow_id)).first()

    @classmethod
    def create(cls, flow_id, name, columns, email):
        flow = cls(flow_id=flow_id, name=name, email=email)
        flow.create_ft(columns)
        db.session.add(flow)
        db.session.commit()
        flow.give_rapidpro_permission()
        return flow

    @classmethod
    def get_columns_from_values(cls, values):
        columns = [{'name': 'phone', 'type': 'STRING'}]

        for v in values:
            columns.append({'name': v.get('label'), 'type': 'STRING'})
        return columns

    def get_updated_columns(self, columns, values):
        cl = [x.get('name') for x in self.__class__.get_columns_from_values(values)]
        if set(cl) == set(columns):
            return columns
        new_cl = set(cl) - set(columns)
        self.update_ft_table(new_cl)
        self.ft_columns = str(cl)
        db.session.add(self)
        db.session.commit()
        return cl

    def update_ft_table(self, columns):
        service = build_service()
        columns = [{'name': x, 'type': 'STRING'} for x in columns]
        for c in columns:
            service.column().insert(tableId=self.ft_id, body=c).execute()

    def create_ft(self, columns):
        service = build_service()
        table = {'name': self.name, 'description': "Rapidpro Flow with ID %s" % self.flow_id, 'isExportable': True,
                 'columns': columns}
        self.ft_columns = str([str(x.get('name')) for x in columns])
        table = service.table().insert(body=table).execute()
        self.ft_id = table.get('tableId')

    def update_fusion_table(self, phone, values):
        service = build_service()
        columns = tuple([str(a) for a in eval(self.ft_columns)])
        columns = tuple([str(a) for a in self.get_updated_columns(columns, values)])
        _order = [str(phone)]
        for c in columns:
            for v in values:
                if v.get('label') == c:
                    _order.append(str(v.get('value')))
                    continue
        _order = tuple(_order)

        sql = 'INSERT INTO %s %s VALUES %s' % (self.ft_id, str(columns), str(_order))
        service.query().sql(sql=sql).execute()

    def give_rapidpro_permission(self):
        email = self.email or RAPIDPRO_EMAIL
        service = build_drive_service()
        body = {'role': 'writer', 'type': 'user', 'emailAddress': email, 'value': email}
        service.permissions().insert(fileId=self.ft_id, body=body, sendNotificationEmails=True).execute()

    def update_email(self, email):
        if email and self.email != email:
            self.email = email
            self.give_rapidpro_permission()
            db.session.add(self)
            db.session.commit()