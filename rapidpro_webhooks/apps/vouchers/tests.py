from flask_testing import TestCase
from stdnum import verhoeff

from rapidpro_webhooks.apps.core.exceptions import VoucherException
from rapidpro_webhooks.apps.vouchers.models import Voucher
from rapidpro_webhooks.core import app, db


class VoucherTestCase(TestCase):
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
        voucher = Voucher.create()
        assert voucher in db.session
        self.assertIsNotNone(voucher.code)
        self.assertIsNone(voucher.redeemed_on)
        self.assertIsNone(voucher.redeemed_by)

    def test_add_external_codes(self):
        codes = ['TE3', '87Y', '90W', 'KJ7']
        initial_count = Voucher.query.count()
        Voucher.add_external_codes(codes)
        self.assertEqual(len(codes), Voucher.query.count() - initial_count)

    def test_redeem(self):
        voucher = Voucher.create()
        assert voucher in db.session
        code = voucher.code
        self.assertIsNone(voucher.redeemed_on)
        self.assertIsNone(voucher.redeemed_by)
        Voucher.redeem(code, self.test_phone, 12345)
        self.assertEqual(voucher.redeemed_by, self.test_phone)
        self.assertIsNotNone(voucher.redeemed_on)

    def test_redeem_redeemed(self):
        voucher = Voucher.create()
        assert voucher in db.session
        code = voucher.code
        Voucher.redeem(code, self.test_phone, 12345)
        self.assertEqual(voucher.redeemed_by, self.test_phone)
        self.assertIsNotNone(voucher.redeemed_on)
        with self.assertRaises(VoucherException):
            Voucher.redeem(code, self.test_phone, 12345)

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
        v = Voucher.create()
        json = {
            'run': u'5921746',
            'phone': u'+12065551212',
            'text': v.code,
            'flow': u'701',
            'weeks_since_last_menses': 0,
            'relayer': u'-1',
            'step': u'396b6731-f9dc-4078-b8c3-46a79524babe',
            'time': u'2014-10-29T17:45:04.291417Z'
        }
        response = self.client.post("/api/v1/voucher/validate", data=json)
        self.assertEquals(response.json, {'validity': 'valid'})
        response = self.client.post("/api/v1/voucher/validate", data=json)
        self.assertEquals(response.json,
                          {'validity': 'invalid', 'reason': 'Attempting to redeem an already redeemed voucher'})
        json.update({'text': '12345'})
        response = self.client.post("/api/v1/voucher/validate", data=json)
        self.assertEquals(response.json,
                          {'validity': 'invalid', 'reason': 'Voucher does not exist'})
