"""address to venue

Revision ID: 132b5354782e
Revises: d450e595654f
Create Date: 2019-11-20 22:09:43.077487

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '132b5354782e'
down_revision = 'd450e595654f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('venues',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('address', sa.String(length=64), nullable=False),
    sa.Column('city', sa.String(length=64), nullable=False),
    sa.Column('state', sa.String(length=2), nullable=False),
    sa.Column('zip_code', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address'),
    sa.UniqueConstraint('city'),
    sa.UniqueConstraint('state'),
    sa.UniqueConstraint('zip_code')
    )
    
    op.add_column('events', sa.Column('venue_id', sa.Integer(), nullable=False))
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.create_foreign_key(None, 'events', 'venues', ['venue_id'], ['id'])
    op.drop_column('events', 'venue')
    op.create_unique_constraint(None, 'users', ['website'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.add_column('events', sa.Column('address_id', sa.INTEGER(), nullable=False))
    op.add_column('events', sa.Column('venue', sa.VARCHAR(length=64), nullable=False))
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.create_foreign_key(None, 'events', 'addresses', ['address_id'], ['id'])
    op.drop_column('events', 'venue_id')
    op.create_table('addresses',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('street_address', sa.VARCHAR(length=64), nullable=False),
    sa.Column('city', sa.VARCHAR(length=64), nullable=False),
    sa.Column('state', sa.VARCHAR(length=2), nullable=False),
    sa.Column('zip_code', sa.VARCHAR(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('city'),
    sa.UniqueConstraint('state'),
    sa.UniqueConstraint('zip_code')
    )
    op.drop_table('venues')
    # ### end Alembic commands ###
