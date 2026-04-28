from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, JSON


class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    sku: Mapped[str] = mapped_column(String, primary_key = True)
    name: Mapped[str] = mapped_column(String, nullable = False)
    description: Mapped[str] = mapped_column(String, nullable = False)
    price_in_cents: Mapped[int] = mapped_column(Integer, nullable = False)
    currency: Mapped[str] = mapped_column(String, nullable = False)
    attributes: Mapped[dict] = mapped_column(JSON, nullable = False)
    estimated_delivery_days: Mapped[int | None] = mapped_column(Integer, nullable = True)
