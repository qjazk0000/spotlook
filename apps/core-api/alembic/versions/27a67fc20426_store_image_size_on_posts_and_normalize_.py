"""store image size on posts and normalize hotspot coords

Revision ID: 27a67fc20426
Revises: d9562680e157
Create Date: 2026-02-10 23:16:47.968391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27a67fc20426'
down_revision: Union[str, Sequence[str], None] = 'd9562680e157'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # posts: image size columns
    op.add_column("posts", sa.Column("image_width", sa.Integer(), nullable=True))
    op.add_column("posts", sa.Column("image_height", sa.Integer(), nullable=True))
    
    # hotspots: enforce normalized range [0, 1]
    op.create_check_constraint(
        "ck_hotspots_x_0_1", "hotspots", "x >= 0 AND x <= 1"
    )
    op.create_check_constraint(
        "ck_hotspots_y_0_1", "hotspots", "y >= 0 AND y <= 1"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_hotspots_y_0_1", "hotspots", type_="check")
    op.drop_constraint("ck_hotspots_x_0_1", "hotspots", type_="check")
    
    op.drop_column("posts", "image_height")
    op.drop_column("posts", "image_width")
