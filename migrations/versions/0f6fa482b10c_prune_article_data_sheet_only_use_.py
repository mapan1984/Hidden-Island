"""prune Article data sheet, only use timestamp

Revision ID: 0f6fa482b10c
Revises: e4e7040f27ce
Create Date: 2018-04-18 11:31:33.357344

"""

# revision identifiers, used by Alembic.
revision = '0f6fa482b10c'
down_revision = 'e4e7040f27ce'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('articles', 'date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articles', sa.Column('date', sa.DATE(), nullable=True))
    # ### end Alembic commands ###
