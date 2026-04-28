from typing import Sequence, Union
import sqlalchemy
from datetime import datetime
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'insert_inventory_rows_revision'
down_revision: Union[str, Sequence[str], None] = "ecb0be80bf25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


rows =  [{"sku": "SKU-NORMAL-001", "available_quantity": 10, "updated_at": datetime.fromisoformat("2026-04-27T10:01:48.917+00:00")},
        {"sku": "SKU-LOW-002", "available_quantity": 1, "updated_at": datetime.fromisoformat("2026-04-27T10:01:48.917+00:00")},
        {"sku": "SKU-HIGH-003", "available_quantity": 100, "updated_at": datetime.fromisoformat("2026-04-21T11:01:48.917+00:00")},
        {"sku": "SKU-NONE-004", "available_quantity": 0, "updated_at": datetime.fromisoformat("2021-03-13T15:11:28.117+00:00")}]

inventory_items_table = sqlalchemy.Table(
    "inventory_items",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("sku", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("available_quantity", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime(timezone=True), nullable=False),
)

def insert_rows(rows) -> None:
    op.bulk_insert(inventory_items_table, rows)

def delete_rows(rows) -> None:
    skus = [row["sku"] for row in rows]
    op.execute(
        inventory_items_table.delete().where(
            inventory_items_table.c.sku.in_(skus)
        )
    )
    
def upgrade() -> None:
    insert_rows(rows)

def downgrade() -> None:
    delete_rows(rows)