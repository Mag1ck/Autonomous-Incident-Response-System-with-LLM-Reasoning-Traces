"""create users table

Revision ID: 83a60977deb7
Revises: insert_inventory_rows_revision
Create Date: 2026-10-14 22:20:16.083067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83a60977deb7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("users",
    sa.Column("user_id", sa.String(), nullable=False),
    sa.Column("first_name", sa.String(), nullable=False),
    sa.Column("last_name", sa.String(), nullable=False),
    sa.Column("email", sa.String(), nullable=False),
    sa.Column("status", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint("user_id"),
    sa.UniqueConstraint("email")
    )


def downgrade() -> None:
    op.drop_table("users")
