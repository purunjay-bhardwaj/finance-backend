from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date
from enum import Enum

class RecordType(str, Enum):
    income = "income"
    expense = "expense"

class RecordCreate(BaseModel):
    amount: float
    type: RecordType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return v

class RecordUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

class RecordResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: date
    notes: Optional[str]
    created_by: int

    class Config:
        from_attributes = True