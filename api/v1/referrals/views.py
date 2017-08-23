import json
from flask import request, redirect, render_template
from flask.ext.login import login_required, current_user
from forms import LoginForm
from models import RefCode, Referral, User
from ..api import api
from ..helpers import create_response
from ..decorators import limit


__author__ = 'kenneth'


@api.route('/referral/create', methods=['POST'])
@limit(max_requests=10000, group="voucher", by='ip')
def create_referral():
    response = {'validity': 'invalid'}
    email = phone = country = name = organization = None
    data = request.json or request.form
    data = dict(data)
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
    code = RefCode.create_code(contact, name, phone, email, organization, country)
    response['code'] = code.ref_code.upper()
    return create_response(response)


@api.route('/referral/refer', methods=['POST'])
@limit(max_requests=10000, group="voucher", by='ip')
def refer_referral():
    response = {'validity': 'invalid'}
    data = request.json or request.form
    data = dict(data)
    code = data.get('text')[0]
    contact = data.get('contact')[0]
    if RefCode.get_by_code(code):
        if not Referral.is_duplicate(contact, code):
            Referral.create(contact, code)
            response['validity'] = 'valid'
    return create_response(response)


@api.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    print form.email.data
    print form.password.data
    if form.validate_on_submit():
        print True
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.login(form.password.data):
            return redirect('/admin')
    return render_template("admin/login.html", form=form)


@api.route('/logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    user.logout()
    return redirect('/admin')