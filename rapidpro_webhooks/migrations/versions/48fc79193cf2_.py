"""empty message

Revision ID: 48fc79193cf2
Revises: 94235923a509
Create Date: 2016-07-11 14:42:28.082772

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = '48fc79193cf2'
down_revision = '94235923a509'


def upgrade():
    op.add_column('fusion_table_flows', sa.Column('email', sa.String(), nullable=True))


def downgrade():
    op.drop_column('fusion_table_flows', 'email')
