from flask import render_template

from rapidpro_webhooks.ui import ui_bp


@ui_bp.route('/', methods=['GET'])
def index():
    return render_template('dashboard.html')
