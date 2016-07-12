import json
from api.v1.db import db
from api.v1.fusiontables.utils import build_service, build_drive_service
from settings.base import RAPIDPRO_EMAIL


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