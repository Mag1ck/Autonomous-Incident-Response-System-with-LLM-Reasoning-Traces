from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    pass

class InventoryItems(Base):
    __tablename__ = "inventory_items"
    sku: Mapped[str] = mapped_column(String, primary_key = True)
    available_quantity: Mapped[int] = mapped_column(Integer, nullable = False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False) 

