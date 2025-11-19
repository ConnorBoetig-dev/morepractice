"""Add is_admin field to users table

Revision ID: a1b2c3d4e5f6
Revises: face74d728c6
Create Date: 2025-11-18 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'face74d728c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_admin column to users table
    # Default: False (regular user)
    # This enables admin panel access and content management
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove is_admin column if rolling back migration
    op.drop_column('users', 'is_admin')
