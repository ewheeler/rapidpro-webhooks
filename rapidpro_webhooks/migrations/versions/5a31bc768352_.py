"""empty message

Revision ID: 5a31bc768352
Revises: b50f86c87339
Create Date: 2016-07-11 10:17:11.692523

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = '5a31bc768352'
down_revision = 'b50f86c87339'


def upgrade():
    op.create_table(
        'fusion_table_flows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flow_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('ft_id', sa.String(), nullable=True),
        sa.Column('ft_columns', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )


def downgrade():
    op.drop_table('fusion_table_flows')
