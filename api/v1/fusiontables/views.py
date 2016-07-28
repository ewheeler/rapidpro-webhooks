import json
from flask import request
from ..api import api
from tasks import update_fusion_table, create_flow_and_update_ft
from ..helpers import create_response
from ..decorators import limit
from models import Flow


__author__ = 'kenneth'

@api.route('/ft/save', methods=['POST'])
@limit(max_requests=10000, group="voucher", by='ip')
def save_run():
    action = 'insert'
    data = request.json or request.form
    phone = data.get('phone')
    flow_id = data.get('flow')
    email = request.args.get('email')
    base_language = data.get('flow_base_language')
    values = json.loads(data.get('values'))

    flow = Flow.get_by_flow(flow_id)
    if flow:
        update_fusion_table.delay(flow.id, phone, values, email, base_language)
    else:
        action = 'create and insert'
        create_flow_and_update_ft.delay(data, email, phone, values, base_language)

    response = {'action': action}
    return create_response(response)
