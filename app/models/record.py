from sqlalchemy import Column, Integer, String, Numeric, Date, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone
import enum

class RecordType(str, enum.Enum):
    income = "income"
    expense = "expense"

class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id         = Column(Integer, primary_key=True, index=True)
    amount     = Column(Numeric(15, 2), nullable=False)
    type       = Column(Enum(RecordType), nullable=False)
    category   = Column(String(100), nullable=False)
    date       = Column(Date, nullable=False)
    notes      = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    creator = relationship("User", backref="records")