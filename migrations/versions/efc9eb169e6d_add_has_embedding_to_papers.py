"""add has_embedding to papers

Revision ID: efc9eb169e6d
Revises: 7bc1b9346a10
Create Date: 2026-09-10 14:48:48.364218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efc9eb169e6d'
down_revision: Union[str, Sequence[str], None] = '7bc1b9346a10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'papers',
        sa.Column('has_embedding', sa.Boolean(), nullable=False, server_default=sa.false())
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('papers', 'has_embedding')