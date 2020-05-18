"""empty message

Revision ID: 29f7009fa84a
Revises: 66c5e17835a0
Create Date: 2016-12-14 16:58:10.567577

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = '29f7009fa84a'
down_revision = '66c5e17835a0'


def upgrade():
    op.create_table(
        'ref_code',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rapidpro_uuid', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=50), nullable=True),
        sa.Column('group', sa.String(length=50), nullable=True),
        sa.Column('country', sa.String(length=50), nullable=True),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=True),
        sa.Column('modified_on', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'fusion_table_flows', sa.Column('created_on', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column(u'fusion_table_flows', 'created_on')
    op.drop_table('ref_code')
