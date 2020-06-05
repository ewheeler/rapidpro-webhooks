import json

from flask import Blueprint, request

from rapidpro_webhooks.apps.core.decorators import limit
from rapidpro_webhooks.apps.core.helpers import create_response
from rapidpro_webhooks.apps.referrals.models import RefCode, Referral

referrals_bp = Blueprint('referrals', __name__)


@referrals_bp.route('/create', methods=['POST'])
@limit(max_requests=10000, group="voucher", by='ip')
def create_referral():
    response = {'validity': 'invalid'}
    email = phone = country = name = organization = None
    data = request.json or request.form
    data = dict(data)

    # check if we are a legacy webhook
    if 'flow_base_language' in data:
        base_lang = data.get('flow_base_language')[0]
        contact = data.get('contact')[0]
        values = json.loads(data.get('values')[0])
        for v in values:
            if v.get('category').get(base_lang).lower() in ['other', 'invalid']:
                continue
            if v.get('label').lower() == 'name':
                name = v.get('text')
            if v.get('label').lower() == 'phone number':
                phone = v.get('rule_value')
            if v.get('label').lower() == 'country':
                country = v.get('text')
            if v.get('label').lower() == 'email':
                email = v.get('text')
            if v.get('label').lower() == 'organization':
                organization = v.get('category').get(base_lang).lower()
    else:
        # the new webhook format
        contact = data.get('contact')['uuid']
        results = data.get('results')
        name = results.get('name')['input']
        phone = results.get('phone_number')['input']
        country = results.get('country')['input']
        organization = results.get('organization')['category']
        email = results.get('email')['input']

    code = RefCode.create_code(contact, name, phone, email, organization, country)
    response['code'] = code.ref_code.upper()
    return create_response(response)


@referrals_bp.route('/refer', methods=['POST'])
@limit(max_requests=10000, group="voucher", by='ip')
def refer_referral():
    response = {'validity': 'invalid'}
    data = request.json or request.form
    data = dict(data)

    # legacy webhook format
    if 'flow_base_language' in data:
        code = data.get('text')[0]
        contact = data.get('contact')[0]
    else:
        code = data.get('results')['refcode']['value']
        contact = data.get('contact')['uuid']

    if RefCode.get_by_code(code):
        if not Referral.is_duplicate(contact, code):
            Referral.create(contact, code)
            response['validity'] = 'valid'
    return create_response(response)


@referrals_bp.route('/', methods=['GET'])
def home():
    return create_response({'app': 'REFERRALS'})
