from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.rbac import require_analyst_or_above, require_any_role
from app.database import get_db
from app.models.record import RecordCategory, RecordType
from app.models.user import User
from app.schemas.record import RecordCreate, RecordFilters, RecordListResponse, RecordResponse, RecordUpdate
from app.services.record_service import RecordService
from datetime import date

router = APIRouter(prefix="/records", tags=["Financial Records"])

@router.post("", response_model=RecordResponse, status_code=201)
def create_record(payload: RecordCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_analyst_or_above)):
    return RecordService(db).create_record(payload, current_user)

@router.get("", response_model=RecordListResponse)
def list_records(
    record_type: RecordType | None = None, category: RecordCategory | None = None,
    date_from: date | None = None, date_to: date | None = None,
    min_amount: float | None = None, max_amount: float | None = None,
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), _: User = Depends(require_any_role),
):
    filters = RecordFilters(record_type=record_type, category=category, date_from=date_from,
                            date_to=date_to, min_amount=min_amount, max_amount=max_amount,
                            page=page, page_size=page_size)
    return RecordService(db).list_records(filters)

@router.get("/{record_id}", response_model=RecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db), _: User = Depends(require_any_role)):
    return RecordService(db).get_record(record_id)

@router.patch("/{record_id}", response_model=RecordResponse)
def update_record(record_id: int, payload: RecordUpdate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_analyst_or_above)):
    return RecordService(db).update_record(record_id, payload, current_user)

@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(require_analyst_or_above)):
    RecordService(db).delete_record(record_id, current_user)