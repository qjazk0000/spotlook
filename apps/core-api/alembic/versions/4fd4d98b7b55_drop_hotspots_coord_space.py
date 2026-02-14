"""drop hotspots coord_space

Revision ID: 4fd4d98b7b55
Revises: a13d80a447d4
Create Date: 2026-02-14 15:45:48.702160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fd4d98b7b55'
down_revision: Union[str, Sequence[str], None] = 'a13d80a447d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("hotspots", "coord_space")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "hotspots",
        sa.Column("coord_space", sa.String(length=20), nullable=False, server_default="normalized"),
    )
