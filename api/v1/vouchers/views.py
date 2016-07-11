import json
from flask import request
from ..api import api
from ..helpers import create_response
from ..decorators import limit
from ..exceptions import VoucherException
from models import Voucher, Flow

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


@api.route('/ft/save', methods=['POST'])
@limit(max_requests=10000, group="voucher", by='ip')
def save_run():
    action = 'insert'
    data = request.json or request.form
    phone = data.get('phone')
    flow_id = data.get('flow')
    email = request.args.get('email')
    values = json.loads(data.get('values'))

    flow = Flow.get_by_flow(flow_id)
    if flow:
        flow.update_email(email)
    else:
        action = 'create and insert'
        flow = Flow.create_from_run(data, email)

    flow.update_fusion_table(phone, values)

    response = {'action': action, 'ft_id': flow.ft_id, 'success': True}
    return create_response(response)
