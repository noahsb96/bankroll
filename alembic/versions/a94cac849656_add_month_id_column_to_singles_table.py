"""Add month_id column to singles table

Revision ID: a94cac849656
Revises: 
Create Date: 2024-09-11 23:56:34.654426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a94cac849656'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('months', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    op.alter_column('months', 'month_year',
               existing_type=sa.DATETIME(),
               nullable=True)
    op.create_index(op.f('ix_months_id'), 'months', ['id'], unique=False)
    op.add_column('singles', sa.Column('month_id', sa.Integer(), nullable=True))
    op.drop_constraint(None, 'singles', type_='foreignkey')
    op.create_foreign_key(None, 'singles', 'months', ['month_id'], ['id'])
    op.drop_column('singles', 'month_bankroll')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('singles', sa.Column('month_bankroll', sa.DATETIME(), nullable=True))
    op.drop_constraint(None, 'singles', type_='foreignkey')
    op.create_foreign_key(None, 'singles', 'months', ['month_bankroll'], ['month_year'])
    op.drop_column('singles', 'month_id')
    op.drop_index(op.f('ix_months_id'), table_name='months')
    op.alter_column('months', 'month_year',
               existing_type=sa.DATETIME(),
               nullable=False)
    op.drop_column('months', 'id')
    # ### end Alembic commands ###