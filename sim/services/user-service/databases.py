from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[str] = mapped_column(String, primary_key = True)
    first_name: Mapped[str] = mapped_column(String, nullable = False)
    last_name: Mapped[str] = mapped_column(String, nullable = False)
    email:  Mapped[str] = mapped_column(String, nullable = False, unique = True)
    status: Mapped[str] = mapped_column(String, nullable = False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)