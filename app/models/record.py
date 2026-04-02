import enum
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecordType(str, enum.Enum):
    income = "income"
    expense = "expense"


class RecordCategory(str, enum.Enum):
    salary = "salary"
    freelance = "freelance"
    investment = "investment"
    food = "food"
    transport = "transport"
    utilities = "utilities"
    entertainment = "entertainment"
    healthcare = "healthcare"
    education = "education"
    shopping = "shopping"
    rent = "rent"
    other = "other"


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    record_type: Mapped[RecordType] = mapped_column(Enum(RecordType), nullable=False, index=True)
    category: Mapped[RecordCategory] = mapped_column(Enum(RecordCategory), nullable=False, index=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    created_by_user: Mapped["User"] = relationship("User", back_populates="records")  # noqa: F821

    def __repr__(self) -> str:
        return f"<FinancialRecord id={self.id} type={self.record_type} amount={self.amount}>"