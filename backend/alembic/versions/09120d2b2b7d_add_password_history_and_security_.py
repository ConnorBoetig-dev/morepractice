"""add_password_history_and_security_enhancements

Revision ID: 09120d2b2b7d
Revises: fd40d9dfebff
Create Date: 2025-11-18 20:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09120d2b2b7d'
down_revision: Union[str, None] = 'b011cddea089'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password_changed_at column to users table
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(), nullable=True))

    # Set default value for existing users
    op.execute("UPDATE users SET password_changed_at = created_at WHERE password_changed_at IS NULL")

    # Create password_history table
    op.create_table('password_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.Column('changed_from_ip', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('change_reason', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_password_history_id'), 'password_history', ['id'], unique=False)
    op.create_index(op.f('ix_password_history_user_id'), 'password_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_password_history_changed_at'), 'password_history', ['changed_at'], unique=False)


def downgrade() -> None:
    # Drop password_history table
    op.drop_index(op.f('ix_password_history_changed_at'), table_name='password_history')
    op.drop_index(op.f('ix_password_history_user_id'), table_name='password_history')
    op.drop_index(op.f('ix_password_history_id'), table_name='password_history')
    op.drop_table('password_history')

    # Remove password_changed_at column from users
    op.drop_column('users', 'password_changed_at')
