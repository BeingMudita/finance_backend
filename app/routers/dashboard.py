from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.rbac import require_analyst_or_above
from app.database import get_db
from app.models.user import User
from app.services.dashboard_service import DashboardService
from datetime import datetime

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def summary(date_from: date | None = None, date_to: date | None = None,
            db: Session = Depends(get_db), _: User = Depends(require_analyst_or_above)):
    return DashboardService(db).get_summary(date_from, date_to)

@router.get("/category-breakdown")
def category_breakdown(db: Session = Depends(get_db), _: User = Depends(require_analyst_or_above)):
    return DashboardService(db).get_category_breakdown()

@router.get("/monthly-trends")
def monthly_trends(year: int = Query(default=datetime.now().year, ge=2000, le=2100),
                   db: Session = Depends(get_db), _: User = Depends(require_analyst_or_above)):
    return DashboardService(db).get_monthly_trends(year)

@router.get("/recent-activity")
def recent_activity(limit: int = Query(10, ge=1, le=50),
                    db: Session = Depends(get_db), _: User = Depends(require_analyst_or_above)):
    from app.schemas.record import RecordResponse
    records = DashboardService(db).get_recent_activity(limit)
    return [RecordResponse.model_validate(r) for r in records]