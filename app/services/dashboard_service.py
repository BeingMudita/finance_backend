from datetime import date
from sqlalchemy import extract, func
from sqlalchemy.orm import Session
from app.models.record import FinancialRecord, RecordType


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self, date_from: date | None = None, date_to: date | None = None):
        q = self.db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)
        if date_from:
            q = q.filter(FinancialRecord.record_date >= date_from)
        if date_to:
            q = q.filter(FinancialRecord.record_date <= date_to)
        return q

    def get_summary(self, date_from: date | None = None, date_to: date | None = None) -> dict:
        q = self._base_query(date_from, date_to)
        rows = self.db.query(
            FinancialRecord.record_type,
            func.sum(FinancialRecord.amount).label("total"),
            func.count(FinancialRecord.id).label("count"),
        ).filter(FinancialRecord.is_deleted == False).group_by(FinancialRecord.record_type).all()

        totals = {row.record_type: {"total": round(row.total, 2), "count": row.count} for row in rows}
        income = totals.get(RecordType.income, {}).get("total", 0.0)
        expenses = totals.get(RecordType.expense, {}).get("total", 0.0)
        return {
            "total_income": income,
            "total_expenses": expenses,
            "net_balance": round(income - expenses, 2),
            "income_count": totals.get(RecordType.income, {}).get("count", 0),
            "expense_count": totals.get(RecordType.expense, {}).get("count", 0),
        }

    def get_category_breakdown(self) -> list[dict]:
        rows = self.db.query(
            FinancialRecord.category,
            FinancialRecord.record_type,
            func.sum(FinancialRecord.amount).label("total"),
        ).filter(FinancialRecord.is_deleted == False).group_by(
            FinancialRecord.category, FinancialRecord.record_type
        ).all()
        return [{"category": r.category, "type": r.record_type, "total": round(r.total, 2)} for r in rows]

    def get_monthly_trends(self, year: int) -> list[dict]:
        rows = self.db.query(
            extract("month", FinancialRecord.record_date).label("month"),
            FinancialRecord.record_type,
            func.sum(FinancialRecord.amount).label("total"),
        ).filter(
            FinancialRecord.is_deleted == False,
            extract("year", FinancialRecord.record_date) == year,
        ).group_by("month", FinancialRecord.record_type).order_by("month").all()
        return [{"month": int(r.month), "type": r.record_type, "total": round(r.total, 2)} for r in rows]

    def get_recent_activity(self, limit: int = 10) -> list:
        records = self.db.query(FinancialRecord).filter(
            FinancialRecord.is_deleted == False
        ).order_by(FinancialRecord.created_at.desc()).limit(limit).all()
        return records