from flask import Blueprint, request

from rapidpro_webhooks.apps.core.decorators import limit
from rapidpro_webhooks.apps.core.exceptions import VoucherException
from rapidpro_webhooks.apps.core.helpers import create_response
from rapidpro_webhooks.apps.vouchers.models import Voucher

voucher_bp = Blueprint('voucher', __name__)


@voucher_bp.route('/', methods=['GET'])
def ureport_bp():
    return create_response({'app': 'Voucher'})


@voucher_bp.route('/validate', methods=['POST'])
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
