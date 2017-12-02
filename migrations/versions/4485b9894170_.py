"""empty message

Revision ID: 4485b9894170
Revises: 
Create Date: 2017-11-26 05:30:31.282731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4485b9894170'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('shoppinglists_name_key', 'shoppinglists', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('shoppinglists_name_key', 'shoppinglists', ['name'])
    # ### end Alembic commands ###
