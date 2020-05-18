"""empty message

Revision ID: dab42a6879dd
Revises: 706b59f6019c
Create Date: 2017-08-22 13:55:56.927686

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = 'dab42a6879dd'
down_revision = '706b59f6019c'


def upgrade():
    op.add_column('user', sa.Column('country', sa.String(), nullable=True))
    op.add_column('user', sa.Column('is_superuser', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('user', 'is_superuser')
    op.drop_column('user', 'country')
