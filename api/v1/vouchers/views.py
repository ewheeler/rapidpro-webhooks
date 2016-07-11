from flask import request
from ..api import api
from models import Voucher
from ..helpers import create_response
from ..decorators import limit
from ..exceptions import VoucherException

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

