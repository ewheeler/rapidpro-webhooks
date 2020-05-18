"""empty message

Revision ID: 81af3f99f387
Revises: 74166be94fd8
Create Date: 2017-10-12 08:52:03.150095

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = '81af3f99f387'
down_revision = '74166be94fd8'


def upgrade():
    op.add_column('user', sa.Column('group', sa.String(), nullable=True))
    op.add_column('user', sa.Column('group_slug', sa.String(), nullable=True))


def downgrade():
    op.drop_column('user', 'group_slug')
    op.drop_column('user', 'group')
