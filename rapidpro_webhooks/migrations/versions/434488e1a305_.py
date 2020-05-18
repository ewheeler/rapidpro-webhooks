"""empty message

Revision ID: 434488e1a305
Revises: None
Create Date: 2015-07-03 10:23:06.454172

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = '434488e1a305'
down_revision = None


def upgrade():
    op.create_table(
        'voucher_vouchers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flow_id', sa.Integer(), nullable=True),
        sa.Column('code', sa.String(length=20), nullable=True),
        sa.Column('redeemed_on', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=True),
        sa.Column('modified_on', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=True),
        sa.Column('redeemed_by', sa.String(length=13), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('voucher_vouchers')
