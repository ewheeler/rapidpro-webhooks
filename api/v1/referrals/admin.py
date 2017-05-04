from flask.ext.admin.contrib.sqla import ModelView


class RefModelView(ModelView):
    can_create = False
    can_delete = False
    column_exclude_list = ['ft_id', 'in_ft', 'last_ft_update', 'ft_row_id', 'modified_on']
    form_excluded_columns = ['ft_id', 'in_ft', 'last_ft_update', 'ft_row_id', 'modified_on', 'created_on']
    can_export = True
    can_set_page_size = True
    column_searchable_list = ['email', 'name', 'phone']
    column_list = ['name', 'phone', 'email', 'group', 'country', 'created_on', 'ref_code', 'ref_count']


class ReferralModelView(ModelView):
    can_delete = False
    can_create = False
    can_export = True
    can_set_page_size = True
    column_exclude_list = ['ref_code']
    column_searchable_list = ['code']

