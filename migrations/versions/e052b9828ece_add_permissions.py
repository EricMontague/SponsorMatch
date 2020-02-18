"""add permissions

Revision ID: e052b9828ece
Revises: 14adae5f3db7
Create Date: 2019-12-07 21:21:44.842903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e052b9828ece'
down_revision = '14adae5f3db7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('permissions', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('roles', 'permissions')
    # ### end Alembic commands ###
