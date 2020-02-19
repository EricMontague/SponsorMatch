"""m profile-photo




Revision ID: 8a8781cb6acd
Revises: fd5b0f09022f
Create Date: 2020-02-03 19:00:30.797223

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a8781cb6acd'
down_revision = 'fd5b0f09022f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_photo_path', sa.Text(), nullable=True))
        batch_op.create_unique_constraint("unique_photo", ['profile_photo_path'])
        batch_op.drop_column('profile_photo')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_photo', sa.TEXT(), nullable=True))
        batch_op.drop_constraint("unique_photo", type_='unique')
        batch_op.drop_column('profile_photo_path')

    # ### end Alembic commands ###