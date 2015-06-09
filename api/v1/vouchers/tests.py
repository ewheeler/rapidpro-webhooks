from flask.ext.testing import TestCase
from stdnum import verhoeff
from api.v1.vouchers.models import Voucher
from api.v1.exceptions import VoucherException
from server import app, db

__author__ = 'kenneth'


class VoucherTestCase(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        return app

    def setUp(self):
        self.test_phone = '2567888123456'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create(self):
        voucher = Voucher.create()
        assert voucher in db.session
        self.assertIsNotNone(voucher.code)
        print voucher.code, "Code of voucher"
        self.assertIsNone(voucher.redeemed_on)
        self.assertIsNone(voucher.redeemed_by)

    def test_redeem(self):
        voucher = Voucher.create()
        assert voucher in db.session
        code = voucher.code
        self.assertIsNone(voucher.redeemed_on)
        self.assertIsNone(voucher.redeemed_by)
        Voucher.redeem(code, self.test_phone)
        self.assertEqual(voucher.redeemed_by, self.test_phone)
        self.assertIsNotNone(voucher.redeemed_on)

    def test_redeem_redeemed(self):
        voucher = Voucher.create()
        assert voucher in db.session
        code = voucher.code
        Voucher.redeem(code, self.test_phone)
        self.assertEqual(voucher.redeemed_by, self.test_phone)
        self.assertIsNotNone(voucher.redeemed_on)
        with self.assertRaises(VoucherException):
            Voucher.redeem(code, self.test_phone)

    def test_generated_code_is_verhoeff_compliant(self):
        code = Voucher.generate_code()
        self.assertEqual(verhoeff.checksum(code), 0)
        code = Voucher.generate_code()
        self.assertEqual(verhoeff.checksum(code), 0)
        code = Voucher.generate_code()
        self.assertEqual(verhoeff.checksum(code), 0)


class TestViews(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_validate_voucher(self):
        headers = {'kenneth': 'matovu'}
        _json = {'run': u'5921746', 'phone': u'+12065551212', 'text': u'1', 'flow': u'701', 'weeks_since_last_menses': 0,
             'relayer': u'-1', 'step': u'396b6731-f9dc-4078-b8c3-46a79524babe',
             'values': u'[{"category": {"eng": "All Responses"}, "time": "2014-10-29T17:45:02.071349Z", "text": "1", "rule_value": "1", "value": "1", "label": "Mother Name"}, '
                       u'[{"category": {"eng": "All Responses"}, "time": "2014-10-29T17:45:02.071349Z", "text": "100014", "rule_value": "1", "value": "100014", "label": "Voucher"}, '
                       u'{"category": {"base": "0 - 36", "eng": "0 - 40"}, "time": "2014-10-29T17:45:02.081099Z", "text": "1", "rule_value": "1", "value": "1.00000000", "label": "Weeks Since Last Menses"}]',
             'time': u'2014-10-29T17:45:04.291417Z',
             'steps': u'[{"node": "3fc6558e-60a2-4eae-926e-c0bfb49a6909", "arrived_on": "2014-10-29T17:44:54.075558Z", "left_on": "2014-10-29T17:44:54.084541Z", "text": "Thank you. What is the mother\'s name?", "type": "A", "value": null}, {"node": "1620d1b9-a10a-4c0a-ab1c-62b28a3bf728", "arrived_on": "2014-10-29T17:44:54.086713Z", "left_on": "2014-10-29T17:45:02.071349Z", "text": "1", "type": "R", "value": "1"}, {"node": "9a10c6b9-a68c-4ed5-b2e0-dca691177332", "arrived_on": "2014-10-29T17:45:02.073199Z", "left_on": "2014-10-29T17:45:02.077586Z", "text": "How many weeks since 1 had her last menstrual period?", "type": "A", "value": null}, {"node": "da353e4b-a0ee-4061-9d30-b990c77c9423", "arrived_on": "2014-10-29T17:45:02.081099Z", "left_on": null, "text": "1", "type": "R", "value": "1"}]'}
        response = self.client.post("/api/v1/voucher/validate", data=_json, headers=headers)
        self.assertEquals(response.json, {'validity': 'valid'})
        response = self.client.post("/api/v1/voucher/validate", data=_json, headers=headers)
        self.assertEquals(response.json,
                          {'validity': 'invalid', 'reason': 'Attempting to redeem an already redeemed voucher'})
