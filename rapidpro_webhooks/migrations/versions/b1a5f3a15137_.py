"""empty message

Revision ID: b1a5f3a15137
Revises: 135e5064a405
Create Date: 2017-01-26 09:45:59.359609

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = 'b1a5f3a15137'
down_revision = '135e5064a405'


def upgrade():
    op.create_table(
        'FT',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ft_id', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'ref_code', sa.Column('in_ft', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column(u'ref_code', 'in_ft')
    op.drop_table('FT')
