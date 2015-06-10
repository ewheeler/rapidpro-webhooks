import json
from flask import request
from ..api import api
from ..decorators import limit
from ..exceptions import VoucherException
from models import Voucher

__author__ = 'kenneth'


@api.route('/voucher/validate', methods=['POST'])
@limit(max_requests=10, group="voucher", by='ip')
def validate_voucher():
    response = {'validity': 'invalid'}
    data = request.json
    if data:
        values = data.get('values')

        if not isinstance(values, list):
            values = json.loads(values)
        code = [value for value in values if value.get('label').lower() == 'voucher'][0]['value']
        phone = data.get('phone')
        try:
            Voucher.redeem(code, phone)
            response['validity'] = 'valid'
        except VoucherException as e:
            response['reason'] = str(e)
    return json.dumps(response)