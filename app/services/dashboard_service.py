from datetime import date, datetime

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models.record import FinancialRecord, RecordType


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def _active_records(self):
        return self.db.query(FinancialRecord).filter(
            FinancialRecord.is_deleted == False  # noqa: E712
        )

    def get_summary(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict:
        q = self.db.query(
            FinancialRecord.record_type,
            func.sum(FinancialRecord.amount).label("total"),
            func.count(FinancialRecord.id).label("count"),
        ).filter(FinancialRecord.is_deleted == False)  # noqa: E712

        if date_from:
            q = q.filter(FinancialRecord.record_date >= date_from)
        if date_to:
            q = q.filter(FinancialRecord.record_date <= date_to)

        rows = q.group_by(FinancialRecord.record_type).all()
        totals = {
            row.record_type: {"total": round(row.total or 0, 2), "count": row.count}
            for row in rows
        }

        income = totals.get(RecordType.income, {}).get("total", 0.0)
        expenses = totals.get(RecordType.expense, {}).get("total", 0.0)

        return {
            "total_income": income,
            "total_expenses": expenses,
            "net_balance": round(income - expenses, 2),
            "income_transactions": totals.get(RecordType.income, {}).get("count", 0),
            "expense_transactions": totals.get(RecordType.expense, {}).get("count", 0),
            "period": {
                "from": str(date_from) if date_from else None,
                "to": str(date_to) if date_to else None,
            },
        }

    def get_category_breakdown(self) -> list[dict]:
        rows = (
            self.db.query(
                FinancialRecord.category,
                FinancialRecord.record_type,
                func.sum(FinancialRecord.amount).label("total"),
                func.count(FinancialRecord.id).label("count"),
            )
            .filter(FinancialRecord.is_deleted == False)  # noqa: E712
            .group_by(FinancialRecord.category, FinancialRecord.record_type)
            .order_by(func.sum(FinancialRecord.amount).desc())
            .all()
        )
        return [
            {
                "category": r.category,
                "type": r.record_type,
                "total": round(r.total or 0, 2),
                "count": r.count,
            }
            for r in rows
        ]

    def get_monthly_trends(self, year: int) -> list[dict]:
        rows = (
            self.db.query(
                extract("month", FinancialRecord.record_date).label("month"),
                FinancialRecord.record_type,
                func.sum(FinancialRecord.amount).label("total"),
                func.count(FinancialRecord.id).label("count"),
            )
            .filter(
                FinancialRecord.is_deleted == False,  # noqa: E712
                extract("year", FinancialRecord.record_date) == year,
            )
            .group_by("month", FinancialRecord.record_type)
            .order_by("month")
            .all()
        )
        return [
            {
                "month": int(r.month),
                "month_name": datetime(year, int(r.month), 1).strftime("%B"),
                "type": r.record_type,
                "total": round(r.total or 0, 2),
                "count": r.count,
            }
            for r in rows
        ]

    def get_weekly_trends(self, year: int) -> list[dict]:
        rows = (
            self.db.query(
                extract("week", FinancialRecord.record_date).label("week"),
                FinancialRecord.record_type,
                func.sum(FinancialRecord.amount).label("total"),
                func.count(FinancialRecord.id).label("count"),
            )
            .filter(
                FinancialRecord.is_deleted == False,  # noqa: E712
                extract("year", FinancialRecord.record_date) == year,
            )
            .group_by("week", FinancialRecord.record_type)
            .order_by("week")
            .all()
        )
        return [
            {
                "week": int(r.week),
                "type": r.record_type,
                "total": round(r.total or 0, 2),
                "count": r.count,
            }
            for r in rows
        ]

    def get_recent_activity(self, limit: int = 10) -> list[FinancialRecord]:
        return (
            self._active_records()
            .order_by(FinancialRecord.created_at.desc())
            .limit(limit)
            .all()
        )