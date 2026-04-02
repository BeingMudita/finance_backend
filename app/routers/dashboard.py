from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.rbac import require_analyst_or_above
from app.database import get_db
from app.models.user import User
from app.schemas.record import RecordResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    summary="Get income, expense, and net balance totals [Analyst, Admin]",
)
def summary(
    date_from: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_above),
):
    return DashboardService(db).get_summary(date_from, date_to)


@router.get(
    "/category-breakdown",
    summary="Get totals grouped by category and type [Analyst, Admin]",
)
def category_breakdown(
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_above),
):
    return DashboardService(db).get_category_breakdown()


@router.get(
    "/monthly-trends",
    summary="Get month-by-month income/expense totals for a given year [Analyst, Admin]",
)
def monthly_trends(
    year: int = Query(
        default=datetime.now().year,
        ge=2000,
        le=2100,
        description="Year to retrieve trends for",
    ),
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_above),
):
    return DashboardService(db).get_monthly_trends(year)


@router.get(
    "/weekly-trends",
    summary="Get week-by-week income/expense totals for a given year [Analyst, Admin]",
)
def weekly_trends(
    year: int = Query(default=datetime.now().year, ge=2000, le=2100),
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_above),
):
    return DashboardService(db).get_weekly_trends(year)


@router.get(
    "/recent-activity",
    response_model=list[RecordResponse],
    summary="Get the most recent financial records [Analyst, Admin]",
)
def recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Number of recent records to return"),
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_above),
):
    records = DashboardService(db).get_recent_activity(limit)
    return [RecordResponse.model_validate(r) for r in records]