"""Fix column alterations for SQLite

Revision ID: e372eccfdf91
Revises: a94cac849656
Create Date: 2024-09-11 23:58:18.528237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e372eccfdf91'
down_revision: Union[str, None] = 'a94cac849656'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'months_new',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('month_year', sa.DateTime, nullable=False),
        sa.Column('bankroll', sa.DECIMAL, nullable=False),
        sa.Column('unit_size', sa.DECIMAL, nullable=False),
    )

    op.execute("""
        INSERT INTO months_new (id, month_year, bankroll, unit_size)
        SELECT id, month_year, bankroll, unit_size
        FROM months
    """)

    op.drop_table('months')

    op.rename_table('months_new', 'months')

def downgrade():
    op.create_table(
        'months_old',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('month_year', sa.DateTime, nullable=True),
        sa.Column('bankroll', sa.DECIMAL, nullable=True),
        sa.Column('unit_size', sa.DECIMAL, nullable=True),
    )

    op.execute("""
        INSERT INTO months_old (id, month_year, bankroll, unit_size)
        SELECT id, month_year, bankroll, unit_size
        FROM months
    """)

    op.drop_table('months')

    op.rename_table('months_old', 'months')
