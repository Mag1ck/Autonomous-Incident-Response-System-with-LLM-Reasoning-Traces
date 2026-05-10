from typing import Sequence, Union
import sqlalchemy
from datetime import datetime
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "insert_catalog_rows_revision"
down_revision: Union[str, Sequence[str], None] = "310dd1028380"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


rows =  [{"sku": "SKU-NORMAL-001", "name": "Smartphone Strawberry 17", "description": "smartphone", "price_in_cents": 500000, "currency": "PLN",
           "attributes": {"color": "yellow", "size": "small", "brand": "strawberry"}, "estimated_delivery_days": 3},
        {"sku": "SKU-LOW-002", "name": "Notebook banana A10", "description": "notebook", "price_in_cents": 900000, "currency": "PLN",
           "attributes": {"color": "black", "size": "normal", "brand": "strawberry"}, "estimated_delivery_days": 10},
        {"sku": "SKU-HIGH-003", "name": "Apopo monitor 4k", "description": "monitor", "price_in_cents": 100050, "currency": "PLN",
           "attributes": {"color": "black", "size": "normal", "brand": "apopo"}, "estimated_delivery_days": 1},
        {"sku": "SKU-NONE-004", "name": "Professional microphone", "description": "microphone", "price_in_cents": 10099, "currency": "PLN",
           "attributes": {"color": "red", "size": "small", "brand": "microphone_brand"}, "estimated_delivery_days": None}]

catalog_table = sqlalchemy.Table(
    "products",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("sku", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("description", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("price_in_cents", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("currency", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("attributes", sqlalchemy.JSON, nullable=False),
    sqlalchemy.Column("estimated_delivery_days", sqlalchemy.Integer, nullable=True)
)

def insert_rows(rows) -> None:
    op.bulk_insert(catalog_table, rows)

def delete_rows(rows) -> None:
    skus = [row["sku"] for row in rows]
    op.execute(
        catalog_table.delete().where(
            catalog_table.c.sku.in_(skus)
        )
    )
    
def upgrade() -> None:
    insert_rows(rows)

def downgrade() -> None:
    delete_rows(rows)