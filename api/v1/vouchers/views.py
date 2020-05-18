from flask import request

from api.v1.api import api
from api.v1.decorators import limit
from api.v1.exceptions import VoucherException
from api.v1.helpers import create_response
from api.v1.vouchers.models import Voucher

__author__ = 'kenneth'


@api.route('/voucher/validate', methods=['POST'])
@limit(max_requests=10000, group="voucher", by='ip')
def validate_voucher():
    response = {'validity': 'invalid'}
    data = request.json or request.form
    code = data.get('text')
    phone = data.get('phone')
    flow = data.get('flow')
    try:
        Voucher.redeem(code, phone, flow)
        response['validity'] = 'valid'
    except VoucherException as e:
        response['reason'] = str(e)
    return create_response(response)
