from flask import request

from rapidpro_webhooks.api.api import api
from rapidpro_webhooks.api.decorators import limit
from rapidpro_webhooks.api.exceptions import VoucherException
from rapidpro_webhooks.api.helpers import create_response
from rapidpro_webhooks.api.vouchers.models import Voucher


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
