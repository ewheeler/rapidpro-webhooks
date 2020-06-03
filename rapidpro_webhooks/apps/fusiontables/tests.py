from flask_testing import TestCase

from rapidpro_webhooks.apps.fusiontables.models import Flow
from rapidpro_webhooks.core import app, db


class FusionTableTestCase(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        return app

    def setUp(self):
        self.test_phone = '+2567888123456'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create(self):
        flow_id = 1
        name = 'test_table'
        columns = [{'name': 'test', 'type': 'STRING'}]
        email = 'rapidprodata+test@gmail.com'
        flow = Flow.create(flow_id, name, columns, email)
        assert flow in db.session
        self.assertEquals(flow.email, email)
        self.assertEquals(flow.flow_id, flow_id)
        self.assertEquals(eval(flow.ft_columns), [x.get('name') for x in columns])

    def test_get_by_flow(self):
        flow_id = 1
        name = 'test_table'
        columns = [{'name': 'test', 'type': 'STRING'}]
        email = 'rapidprodata+test@gmail.com'
        in_flow = Flow.create(flow_id, name, columns, email)
        flow = Flow.get_by_flow(flow_id)
        self.assertEquals(in_flow.id, flow.id)

    def test_create_from_run(self):
        data = {'run': [u'155'], 'relayer': [u'-1'], 'text': [u'gse4twt'], 'flow': u'19', 'phone': u'+12065550100',
                'step': [u'ed49df88-404f-4e21-bc74-78c8ef6b9265'],
                'values': u'[{"category": {"eng": "All Responses"}, '
                          u'"node": "25cc302c-f569-4a23-8f8a-0c10732b44dc", "time": "2016-07-12T13:06:48.937803Z",'
                          u' "text": "asafater", "rule_value": "asafater", "value": "asafater", "label": "name"}, '
                          u'{"category": {"eng": "All Responses"}, "node": "861ebab6-0129-4739-a609-36bb60ff0a66", '
                          u'"time": "2016-07-12T13:06:50.189755Z", "text": "twfggsg", "rule_value": "twfggsg", '
                          u'"value": "twfggsg", "label": "want"}, {"category": {"eng": "All Responses"}, '
                          u'"node": "d7cae705-1b77-474f-8946-588f631cedbb", "time": "2016-07-12T13:06:52.343391Z", '
                          u'"text": "gse4twt", "rule_value": "gse4twt", "value": "gse4twt", "label": "reason"}]',
                'time': [u'2016-07-12T13:06:52.387647Z'], 'steps': [u'[{"node": "19af6b8c-d5d3-43f8-b1f8-7e2728d9cac7",'
                                                                    u' "arrived_on": "2016-07-12T13:06:46.593063Z", '
                                                                    u'"left_on": "2016-07-12T13:06:46.608539Z", '
                                                                    u'"text": "What is your name", "type": "A", '
                                                                    u'"value": null}, '
                                                                    u'{"node": "25cc302c-f569-4a23-8f8a-0c10732b44dc",'
                                                                    u' "arrived_on": "2016-07-12T13:06:46.608539Z", '
                                                                    u'"left_on": "2016-07-12T13:06:48.937803Z", '
                                                                    u'"text": "asafater", "type": "R",'
                                                                    u' "value": "asafater"}, '
                                                                    u'{"node": "b01e1930-880e-4546-833d-0bf3a7f14cf9", '
                                                                    u'"arrived_on": "2016-07-12T13:06:48.938735Z",'
                                                                    u' "left_on": "2016-07-12T13:06:49.016967Z",'
                                                                    u' "text": "What do you want?", "type": "A",'
                                                                    u' "value": null}, '
                                                                    u'{"node": "861ebab6-0129-4739-a609-36bb60ff0a66",'
                                                                    u' "arrived_on": "2016-07-12T13:06:49.016967Z",'
                                                                    u' "left_on": "2016-07-12T13:06:50.189755Z",'
                                                                    u' "text": "twfggsg", "type": "R",'
                                                                    u' "value": "twfggsg"},'
                                                                    u' {"node": "62e516d2-4e03-45c4-a02b-5d89f0e17254",'
                                                                    u' "arrived_on": "2016-07-12T13:06:50.190754Z",'
                                                                    u' "left_on": "2016-07-12T13:06:50.258417Z",'
                                                                    u' "text": "Why", "type": "A", "value": null},'
                                                                    u' {"node": "d7cae705-1b77-474f-8946-588f631cedbb",'
                                                                    u' "arrived_on": "2016-07-12T13:06:50.258417Z",'
                                                                    u' "left_on": "2016-07-12T13:06:52.343391Z",'
                                                                    u' "text": "gse4twt", "type": "R",'
                                                                    u' "value": "gse4twt"},'
                                                                    u' {"node": "ed49df88-404f-4e21-bc74-78c8ef6b9265",'
                                                                    u' "arrived_on": "2016-07-12T13:06:52.344270Z",'
                                                                    u' "left_on": null, "text": null, "type": "A",'
                                                                    u' "value": null}]'],
                'channel': [u'-1']}
        email = 'rapidprodata+test@gmail.com'
        flow = Flow.create_from_run(data, email)
        assert flow in db.session
        self.assertEquals(str(flow.flow_id), data.get('flow'))

    def test_get_columns_from_values(self):
        values = [{"category": {"eng": "All Responses"}, "node": "25cc302c-f569-4a23-8f8a-0c10732b44dc",
                   "time": "2016-07-12T13:06:48.937803Z", "text": "asafater", "rule_value": "asafater",
                   "value": "asafater", "label": "name"}, {"category": {"eng": "All Responses"},
                                                           "node": "861ebab6-0129-4739-a609-36bb60ff0a66",
                                                           "time": "2016-07-12T13:06:50.189755Z",
                                                           "text": "twfggsg", "rule_value": "twfggsg",
                                                           "value": "twfggsg", "label": "want"},
                  {"category": {"eng": "All Responses"},
                   "node": "d7cae705-1b77-474f-8946-588f631cedbb", "time": "2016-07-12T13:06:52.343391Z",
                   "text": "gse4twt", "rule_value": "gse4twt", "value": "gse4twt", "label": "reason"}]
        columns = Flow.get_columns_from_values(values)
        self.assertEquals(columns, [{'name': 'phone', 'type': 'STRING'},
                                    {'name': 'name (value)', 'type': 'STRING'},
                                    {'name': 'name (category)', 'type': 'STRING'},
                                    {'name': 'want (value)', 'type': 'STRING'},
                                    {'name': 'want (category)', 'type': 'STRING'},
                                    {'name': 'reason (value)', 'type': 'STRING'},
                                    {'name': 'reason (category)', 'type': 'STRING'}
                                    ])
