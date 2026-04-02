from sqlalchemy.orm import Session

from app.core.exceptions import AppError, NotFoundError
from app.models.record import FinancialRecord
from app.models.user import User, UserRole
from app.schemas.record import (
    RecordCreate,
    RecordFilters,
    RecordListResponse,
    RecordResponse,
    RecordUpdate,
)
from fastapi import status


class RecordService:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_404(self, record_id: int) -> FinancialRecord:
        record = self.db.query(FinancialRecord).filter(
            FinancialRecord.id == record_id,
            FinancialRecord.is_deleted == False,  # noqa: E712
        ).first()
        if not record:
            raise NotFoundError("FinancialRecord", record_id)
        return record

    def create_record(self, payload: RecordCreate, current_user: User) -> RecordResponse:
        record = FinancialRecord(
            amount=payload.amount,
            record_type=payload.record_type,
            category=payload.category,
            record_date=payload.record_date,
            notes=payload.notes,
            description=payload.description,
            created_by=current_user.id,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return RecordResponse.model_validate(record)

    def get_record(self, record_id: int) -> RecordResponse:
        return RecordResponse.model_validate(self._get_or_404(record_id))

    def list_records(self, filters: RecordFilters) -> RecordListResponse:
        query = self.db.query(FinancialRecord).filter(
            FinancialRecord.is_deleted == False  # noqa: E712
        )

        if filters.record_type:
            query = query.filter(FinancialRecord.record_type == filters.record_type)
        if filters.category:
            query = query.filter(FinancialRecord.category == filters.category)
        if filters.date_from:
            query = query.filter(FinancialRecord.record_date >= filters.date_from)
        if filters.date_to:
            query = query.filter(FinancialRecord.record_date <= filters.date_to)
        if filters.min_amount:
            query = query.filter(FinancialRecord.amount >= filters.min_amount)
        if filters.max_amount:
            query = query.filter(FinancialRecord.amount <= filters.max_amount)

        total = query.count()
        records = (
            query.order_by(FinancialRecord.record_date.desc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
            .all()
        )
        return RecordListResponse(
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            items=[RecordResponse.model_validate(r) for r in records],
        )

    def update_record(self, record_id: int, payload: RecordUpdate, current_user: User) -> RecordResponse:
        record = self._get_or_404(record_id)
        # Non-admins can only update their own records
        if current_user.role != UserRole.admin and record.created_by != current_user.id:
            raise AppError("You can only modify your own records", status.HTTP_403_FORBIDDEN)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        self.db.commit()
        self.db.refresh(record)
        return RecordResponse.model_validate(record)

    def delete_record(self, record_id: int, current_user: User) -> None:
        record = self._get_or_404(record_id)
        if current_user.role != UserRole.admin and record.created_by != current_user.id:
            raise AppError("You can only delete your own records", status.HTTP_403_FORBIDDEN)
        record.is_deleted = True
        self.db.commit()