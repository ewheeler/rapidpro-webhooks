"""empty message

Revision ID: 706b59f6019c
Revises: 2fcde1cbe141
Create Date: 2017-08-22 11:44:27.783612

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = '706b59f6019c'
down_revision = '2fcde1cbe141'


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('authenticated', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )


def downgrade():
    op.drop_table('user')
