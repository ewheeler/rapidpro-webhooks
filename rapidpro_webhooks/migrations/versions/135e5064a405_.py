"""empty message

Revision ID: 135e5064a405
Revises: f14a665a1c57
Create Date: 2017-01-25 16:15:54.175903

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = '135e5064a405'
down_revision = 'f14a665a1c57'


def upgrade():
    op.add_column('ref_code', sa.Column('last_ft_update', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column('ref_code', 'last_ft_update')
