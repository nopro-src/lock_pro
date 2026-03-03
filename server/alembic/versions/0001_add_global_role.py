"""add global_role to accounts

Revision ID: 0001_add_global_role
Revises: 
Create Date: 2026-02-27
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_add_global_role"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite-safe: add as String with default
    with op.batch_alter_table("accounts") as batch_op:
        batch_op.add_column(
            sa.Column("global_role", sa.String(length=16), nullable=False, server_default="USER")
        )
        batch_op.create_index("ix_accounts_global_role", ["global_role"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("accounts") as batch_op:
        batch_op.drop_index("ix_accounts_global_role")
        batch_op.drop_column("global_role")