import json
from collections import OrderedDict
from datetime import datetime

from ordered_set import OrderedSet

from rapidpro_webhooks.apps.core.db import db
from rapidpro_webhooks.apps.fusiontables.utils import build_drive_service, build_service
from rapidpro_webhooks.settings import RAPIDPRO_EMAIL


class Flow(db.Model):
    __tablename__ = 'fusion_table_flows'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    flow_id = db.Column(db.Integer)
    name = db.Column(db.String)
    ft_id = db.Column(db.String)
    ft_columns = db.Column(db.String)
    email = db.Column(db.String, nullable=True)
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    @classmethod
    def create_from_run(cls, run, email):
        flow_id = run.get('flow')
        flow_name = run.get('flow_name')

        values = json.loads(run.get('values'))
        columns = cls.get_columns_from_values(values)

        flow = cls.create(flow_id, flow_name, columns, email)
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
        n = []
        for v in values:
            if v.get('node') in n:
                continue
            columns.append({'name': '%s (value)' % v.get('label'), 'type': 'STRING'})
            columns.append({'name': '%s (category)' % v.get('label'), 'type': 'STRING'})
            n.append(v.get('node'))
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
        return [service.column().insert(tableId=self.ft_id, body=c).execute() for c in columns]

    def create_ft(self, columns):
        service = build_service()
        table = {'name': self.name, 'description': "Rapidpro Flow with ID %s" % self.flow_id, 'isExportable': True,
                 'columns': columns}
        self.ft_columns = str([str(x.get('name')) for x in columns])
        table = service.table().insert(body=table).execute()
        self.ft_id = table.get('tableId')
        return table

    def update_fusion_table(self, phone, values, base_language):
        service = build_service()
        columns = tuple([str(a) for a in eval(self.ft_columns)])
        columns = tuple([str(a) for a in self.get_updated_columns(columns, values)])
        _order = [str(phone)]
        nodes = OrderedDict()
        for c in columns:
            if c == 'phone':
                continue
            label = c.rstrip("(value)").strip()
            for v in values:
                n = v.get('node')
                if v.get('label') == label:
                    category = str(v.get('category').get(base_language))
                    nodes[n] = [str(v.get('value')), category]

        for _v in nodes.values():
            _order.extend(_v)

        sql = 'INSERT INTO %s %s VALUES %s' % (self.ft_id, str(tuple(OrderedSet(columns))), str(tuple(_order)))
        return service.query().sql(sql=sql).execute()

    def give_rapidpro_permission(self):
        email = self.email or RAPIDPRO_EMAIL
        service = build_drive_service()
        body = {'role': 'writer', 'type': 'user', 'emailAddress': email, 'value': email}
        return service.permissions().insert(fileId=self.ft_id, body=body, sendNotificationEmails=True).execute()

    def update_email(self, email):
        if email and self.email != email:
            self.email = email
            self.give_rapidpro_permission()
            db.session.add(self)
            db.session.commit()
        return self.email
