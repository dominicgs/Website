"""

Revision ID: cb60592bbc80
Revises: 0c41275c0244
Create Date: 2018-03-10 02:24:34.528786

"""

# revision identifiers, used by Alembic.
revision = 'cb60592bbc80'
down_revision = '0c41275c0244'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('proposal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('age_range', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('participant_equipment', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('valid_dbs', sa.Boolean(), nullable=False, server_default=expression.false()))

    with op.batch_alter_table('proposal_version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('age_range', sa.String(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('participant_equipment', sa.String(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('valid_dbs', sa.Boolean(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('proposal_version', schema=None) as batch_op:
        batch_op.drop_column('valid_dbs')
        batch_op.drop_column('participant_equipment')
        batch_op.drop_column('age_range')

    with op.batch_alter_table('proposal', schema=None) as batch_op:
        batch_op.drop_column('valid_dbs')
        batch_op.drop_column('participant_equipment')
        batch_op.drop_column('age_range')

    # ### end Alembic commands ###
