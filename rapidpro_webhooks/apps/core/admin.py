from flask import redirect, request

from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


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
        return redirect("/login?next=%s" % request.url)
