from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Float, Boolean, JSON
from datetime import datetime


class Base(DeclarativeBase):
    pass

class Sku(Base):
    __tablename__ = "Stock_keeping_unit"
    sku: Mapped[str] = mapped_column(String, primary_key = True)
    name: Mapped[str] = mapped_column(String, nullable = False)
    description: Mapped[str] = mapped_column(String, nullable = False)
    price: Mapped[float] = mapped_column(Float, nullable = False)
    currency: Mapped[str] = mapped_column(String, nullable = False)
    available_quantity: Mapped[int] = mapped_column(Integer, nullable = False)
    in_stock: Mapped[bool] = mapped_column(Boolean, nullable = False)
    attributes: Mapped[dict] = mapped_column(JSON, nullable = False)
    estimated_delivery_days: Mapped[int] = mapped_column(Integer, nullable = False)
