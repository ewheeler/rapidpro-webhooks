from flask import redirect, request
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import current_user

from api.v1.referrals.models import RefCode


class RefModelView(ModelView):
    can_create = False
    can_delete = False
    column_exclude_list = ['ft_id', 'in_ft', 'last_ft_update', 'ft_row_id', 'modified_on']
    form_excluded_columns = ['ft_id', 'in_ft', 'last_ft_update', 'ft_row_id', 'modified_on', 'created_on']
    can_export = True
    can_set_page_size = True
    column_searchable_list = ['email', 'name', 'phone']
    column_list = ['name', 'phone', 'email', 'group', 'country', 'created_on', 'ref_code', 'ref_count']

    def get_query(self):
        if current_user.is_superuser:
            return super(RefModelView, self).get_query()
        return super(RefModelView, self).get_query().filter(RefCode.country == current_user.country)\
            .filter(RefCode.group == current_user.group)

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/api/v1/login?next=%s" % request.url)


class ReferralModelView(ModelView):
    can_delete = False
    can_create = False
    can_export = True
    can_set_page_size = True
    column_exclude_list = ['ref_code']
    column_searchable_list = ['code']

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/api/v1/login?next=%s" % request.url)


class UserModelView(ModelView):
    can_delete = False
    can_create = True
    can_edit = True
    can_export = False
    column_exclude_list = ['password', 'authenticated']
    form_excluded_columns = ['authenticated', 'country_slug', 'group_slug']
    can_set_page_size = True

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.superuser
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/api/v1/login?next=%s" % request.url)
