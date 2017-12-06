"""

Revision ID: bd431f350ab1
Revises: 2d04d9916f15
Create Date: 2017-12-06 04:23:22.850108

"""

# revision identifiers, used by Alembic.
revision = 'bd431f350ab1'
down_revision = '2d04d9916f15'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('order', sa.Integer(), nullable=True))

    with op.batch_alter_table('product_group', schema=None) as batch_op:
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(),
               nullable=False)

    with op.batch_alter_table('purchase', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_id', sa.Integer(), nullable=False))
        batch_op.alter_column('price_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.create_foreign_key(batch_op.f('fk_purchase_product_id_product'), 'product', ['product_id'], ['id'])

    with op.batch_alter_table('purchase_version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_id', sa.Integer(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_version', schema=None) as batch_op:
        batch_op.drop_column('product_id')

    with op.batch_alter_table('purchase', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_purchase_product_id_product'), type_='foreignkey')
        batch_op.alter_column('price_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.drop_column('product_id')

    with op.batch_alter_table('product_group', schema=None) as batch_op:
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(),
               nullable=True)

    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('order')

    # ### end Alembic commands ###
