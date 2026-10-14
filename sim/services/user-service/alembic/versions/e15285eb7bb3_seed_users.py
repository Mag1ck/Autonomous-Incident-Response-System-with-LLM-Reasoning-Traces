"""seed users

Revision ID: e15285eb7bb3
Revises: 83a60977deb7
Create Date: 2026-10-14 22:20:21.809153

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e15285eb7bb3"
down_revision: Union[str, Sequence[str], None] = "83a60977deb7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


rows = [
    {"user_id": "user-001", "first_name": "Jan", "last_name": "Nowak", "email": "jan.nowak@example.com",
     "status": "active",
     "created_at": datetime.fromisoformat("2026-10-10T20:33:05Z"),
     "updated_at": datetime.fromisoformat("2026-10-11T02:13:15Z")},
    {"user_id": "user-002", "first_name": "Antoine", "last_name": "Kowalski", "email": "antoine.kowalski@example.com",
     "status": "active",
     "created_at": datetime.fromisoformat("2026-10-11T20:33:05Z"),
     "updated_at": datetime.fromisoformat("2026-10-12T02:13:15Z")},
    {"user_id": "user-003", "first_name": "Mark", "last_name": "Lewandowski", "email": "mark.lewandowski@example.com",
     "status": "active",
     "created_at": datetime.fromisoformat("2026-10-12T11:33:05Z"),
     "updated_at": datetime.fromisoformat("2026-10-13T02:13:15Z")},
    {"user_id": "user-004", "first_name": "Peter", "last_name": "Kowalenko", "email": "peter.kowalenko@example.com",
     "status": "blocked",
     "created_at": datetime.fromisoformat("2026-10-01T02:13:15Z"),
     "updated_at": datetime.fromisoformat("2026-10-01T02:13:15Z")},
]

users_table = sa.Table(
    "users",
    sa.MetaData(),
    sa.Column("user_id", sa.String, primary_key=True),
    sa.Column("first_name", sa.String, nullable=False),
    sa.Column("last_name", sa.String, nullable=False),
    sa.Column("email", sa.String, nullable=False, unique=True),
    sa.Column("status", sa.String, nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)


def insert_rows(rows) -> None:
    op.bulk_insert(users_table, rows)


def delete_rows(rows) -> None:
    ids = [row["user_id"] for row in rows]
    op.execute(
        users_table.delete().where(
            users_table.c.user_id.in_(ids)
        )
    )


def upgrade() -> None:
    insert_rows(rows)


def downgrade() -> None:
    delete_rows(rows)