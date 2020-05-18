"""empty message

Revision ID: 74166be94fd8
Revises: dab42a6879dd
Create Date: 2017-08-22 14:21:54.818028

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = '74166be94fd8'
down_revision = 'dab42a6879dd'


def upgrade():
    op.add_column('ref_code', sa.Column('country_slug', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('country_slug', sa.String(), nullable=True))


def downgrade():
    op.drop_column('user', 'country_slug')
    op.drop_column('ref_code', 'country_slug')
