import json
from flask import request
from ..api import api
from ..decorators import limit
from ..exceptions import VoucherException
from ..helpers import create_response
from models import Voucher

__author__ = 'kenneth'


@api.route('/voucher/validate', methods=['POST'])
def validate_voucher():
    response = {'validity': 'invalid'}
    data = request.json
    if data:
        values = data.get('values')
        code = [value for value in values
                 if value.get('label') == 'voucher'][0]['value']
        phone = data.get('phone')
        try:
            Voucher.redeem(code, phone)
            response['validity'] = 'valid'
        except VoucherException as e:
            response['reason'] = str(e)
    return json.dumps(response)