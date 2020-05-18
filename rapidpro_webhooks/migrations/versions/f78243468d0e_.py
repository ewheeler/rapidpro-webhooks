"""empty message

Revision ID: f78243468d0e
Revises: 29f7009fa84a
Create Date: 2016-12-19 17:04:52.576384

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = 'f78243468d0e'
down_revision = '29f7009fa84a'


def upgrade():
    op.create_table(
        'referral',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rapidpro_uuid', sa.String(length=50), nullable=True),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('referral')
