import json

from flask import request

from rapidpro_webhooks.api.api import api
from rapidpro_webhooks.api.decorators import limit
from rapidpro_webhooks.api.fusiontables.models import Flow
from rapidpro_webhooks.api.fusiontables.tasks import create_flow_and_update_ft, update_fusion_table
from rapidpro_webhooks.api.helpers import create_response


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
