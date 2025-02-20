"""Add code and sqm to branch default value

Revision ID: 99f554840030
Revises: e28ccde228b1
Create Date: 2025-01-19 17:57:09.202287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99f554840030'
down_revision = 'e28ccde228b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('branch', schema=None) as batch_op:
        batch_op.add_column(sa.Column('code', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('sqm', sa.Float(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('branch', schema=None) as batch_op:
        batch_op.drop_column('sqm')
        batch_op.drop_column('code')

    # ### end Alembic commands ###
