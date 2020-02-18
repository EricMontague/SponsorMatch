"""remove metrics

Revision ID: b5505585c575
Revises: e07f4edd8bf8
Create Date: 2020-01-23 23:20:41.683561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5505585c575'
down_revision = 'e07f4edd8bf8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('metrics')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('metrics',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('total_sales', sa.NUMERIC(precision=4, scale=2), nullable=False),
    sa.Column('num_packages', sa.INTEGER(), nullable=False),
    sa.Column('num_packages_sold', sa.INTEGER(), nullable=False),
    sa.Column('event_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
