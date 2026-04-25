from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    pass

class OrderTable(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key = True)
    user_id: Mapped[str] = mapped_column(String, nullable = False)
    sku: Mapped[str] = mapped_column(String, nullable = False)
    quantity: Mapped[int] = mapped_column(Integer, nullable = False)
    order_status: Mapped[str] = mapped_column(String, nullable = False)
    payment_status: Mapped[str] = mapped_column(String, nullable = False)
    fraud_status: Mapped[str] = mapped_column(String, nullable = False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)
    rejection_reason: Mapped[str | None] = mapped_column(String, nullable = True)

