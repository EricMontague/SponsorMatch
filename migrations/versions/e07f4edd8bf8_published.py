"""published

Revision ID: e07f4edd8bf8
Revises: c4724927a36d
Create Date: 2020-01-23 21:58:09.383625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e07f4edd8bf8'
down_revision = 'c4724927a36d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('published', sa.Boolean(), nullable=False))
        batch_op.drop_column('live')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('live', sa.BOOLEAN(), nullable=False))
        batch_op.drop_column('published')

    # ### end Alembic commands ###
