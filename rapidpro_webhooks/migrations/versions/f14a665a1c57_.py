"""empty message

Revision ID: f14a665a1c57
Revises: f78243468d0e
Create Date: 2017-01-12 08:37:41.369580

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = 'f14a665a1c57'
down_revision = 'f78243468d0e'


def upgrade():
    op.add_column('ref_code', sa.Column('ft_id', sa.String(length=100), nullable=True))
    op.add_column('referral', sa.Column('created_on',
                                        sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=True))
    op.add_column('referral', sa.Column('ref_code', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('referral', 'ref_code')
    op.drop_column('referral', 'created_on')
    op.drop_column('ref_code', 'ft_id')
