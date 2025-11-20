"""simplify_achievement_avatar_system

Simplify achievement and avatar system by removing unnecessary fields:
- Remove rarity, is_hidden, display_order, badge_icon_url, unlocks_avatar_id from achievements
- Remove rarity, is_default, display_order from avatars

Revision ID: c1d2e3f4g5h6
Revises: 09120d2b2b7d
Create Date: 2025-11-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4g5h6'
down_revision: Union[str, None] = '09120d2b2b7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Simplify achievement and avatar tables

    IMPORTANT: Before running this migration:
    1. Backup your database
    2. Clear old achievement/avatar data if needed
    3. Be prepared to re-seed with the new simplified data
    """

    # ================================================
    # ACHIEVEMENTS TABLE
    # ================================================
    # Remove: rarity, is_hidden, display_order, badge_icon_url, unlocks_avatar_id

    op.drop_column('achievements', 'rarity')
    op.drop_column('achievements', 'is_hidden')
    op.drop_column('achievements', 'display_order')
    op.drop_column('achievements', 'badge_icon_url')

    # Drop the foreign key constraint and column for unlocks_avatar_id
    # Note: The constraint name might vary; adjust if needed
    op.drop_constraint('achievements_unlocks_avatar_id_fkey', 'achievements', type_='foreignkey')
    op.drop_column('achievements', 'unlocks_avatar_id')

    # ================================================
    # AVATARS TABLE
    # ================================================
    # Remove: rarity, is_default, display_order

    op.drop_column('avatars', 'rarity')
    op.drop_column('avatars', 'is_default')
    op.drop_column('avatars', 'display_order')


def downgrade() -> None:
    """
    Restore the removed columns

    Note: This will restore the columns but not the original data.
    You'll need to restore from backup if you need the old data.
    """

    # ================================================
    # AVATARS TABLE (reverse order)
    # ================================================
    op.add_column('avatars', sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('avatars', sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('avatars', sa.Column('rarity', sa.String(), nullable=True))

    # ================================================
    # ACHIEVEMENTS TABLE (reverse order)
    # ================================================
    op.add_column('achievements', sa.Column('unlocks_avatar_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'achievements_unlocks_avatar_id_fkey',
        'achievements',
        'avatars',
        ['unlocks_avatar_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.add_column('achievements', sa.Column('badge_icon_url', sa.String(), nullable=True))
    op.add_column('achievements', sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('achievements', sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('achievements', sa.Column('rarity', sa.String(), nullable=False, server_default='common'))
