"""add_icon_rarity_criteria_exam_type_to_achievements

Revision ID: b011cddea089
Revises: a1b2c3d4e5f6
Create Date: 2025-11-18 19:46:55.919971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b011cddea089'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add icon column (required, default emoji)
    op.add_column('achievements', sa.Column('icon', sa.String(), nullable=False, server_default='🏆'))

    # Add rarity column (required, default 'common')
    op.add_column('achievements', sa.Column('rarity', sa.String(), nullable=False, server_default='common'))

    # Add criteria_exam_type column (optional, for exam-specific achievements)
    op.add_column('achievements', sa.Column('criteria_exam_type', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove the added columns in reverse order
    op.drop_column('achievements', 'criteria_exam_type')
    op.drop_column('achievements', 'rarity')
    op.drop_column('achievements', 'icon')
