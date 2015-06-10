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
    data = request.json or request.form
    code = data.get('text')
    phone = data.get('phone')
    try:
        Voucher.redeem(code, phone)
        response['validity'] = 'valid'
    except VoucherException as e:
        response['reason'] = str(e)
    return json.dumps(response)
