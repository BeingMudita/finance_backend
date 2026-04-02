from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.models.record import RecordCategory, RecordType


class RecordCreate(BaseModel):
    amount: float = Field(gt=0, description="Amount must be greater than 0")
    record_type: RecordType
    category: RecordCategory
    record_date: date
    notes: str | None = Field(default=None, max_length=2000)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float) -> float:
        return round(v, 2)


class RecordUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    record_type: RecordType | None = None
    category: RecordCategory | None = None
    record_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float | None) -> float | None:
        return round(v, 2) if v is not None else None


class RecordResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    amount: float
    record_type: RecordType
    category: RecordCategory
    record_date: date
    notes: str | None
    description: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime


class RecordListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RecordResponse]


class RecordFilters(BaseModel):
    record_type: RecordType | None = None
    category: RecordCategory | None = None
    date_from: date | None = None
    date_to: date | None = None
    min_amount: float | None = Field(default=None, gt=0)
    max_amount: float | None = Field(default=None, gt=0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)