"""empty message

Revision ID: 94235923a509
Revises: 5a31bc768352
Create Date: 2016-07-11 10:22:32.763269

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa  # noqa
from alembic import op

revision = '94235923a509'
down_revision = '5a31bc768352'


def upgrade():
    op.create_unique_constraint(None, 'fusion_table_flows', ['id'])


def downgrade():
    op.drop_constraint(None, 'fusion_table_flows', type_='unique')
