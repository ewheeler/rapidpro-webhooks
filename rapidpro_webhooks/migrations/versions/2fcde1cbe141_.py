"""empty message

Revision ID: 2fcde1cbe141
Revises: b1a5f3a15137
Create Date: 2017-01-26 10:18:02.021739

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = '2fcde1cbe141'
down_revision = 'b1a5f3a15137'


def upgrade():
    op.add_column('ref_code', sa.Column('ft_row_id', sa.String(length=100), nullable=True))


def downgrade():
    op.drop_column('ref_code', 'ft_row_id')
