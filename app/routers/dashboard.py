from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.record import FinancialRecord, RecordType
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(
        func.coalesce(func.sum(case((FinancialRecord.type == RecordType.income, FinancialRecord.amount), else_=0)), 0).label("total_income"),
        func.coalesce(func.sum(case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount), else_=0)), 0).label("total_expenses")
    ).filter(FinancialRecord.deleted_at == None).one()

    total_income = float(result.total_income)
    total_expenses = float(result.total_expenses)

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": total_income - total_expenses
    }

@router.get("/categories")
def get_category_totals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("analyst", "admin"))
):
    results = db.query(
        FinancialRecord.category,
        FinancialRecord.type,
        func.sum(FinancialRecord.amount).label("total"),
        func.count(FinancialRecord.id).label("count")
    ).filter(
        FinancialRecord.deleted_at == None
    ).group_by(
        FinancialRecord.category,
        FinancialRecord.type
    ).order_by(func.sum(FinancialRecord.amount).desc()).all()

    return {"data": [
        {"category": r.category, "type": r.type, "total": float(r.total), "count": r.count}
        for r in results
    ]}

@router.get("/recent")
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = db.query(FinancialRecord).filter(
        FinancialRecord.deleted_at == None
    ).order_by(
        FinancialRecord.date.desc(),
        FinancialRecord.created_at.desc()
    ).limit(limit).all()

    return {"data": [
        {
            "id": r.id,
            "amount": float(r.amount),
            "type": r.type,
            "category": r.category,
            "date": str(r.date),
            "notes": r.notes
        } for r in records
    ]}

@router.get("/trends/monthly")
def get_monthly_trends(
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("analyst", "admin"))
):
    results = db.query(
        func.to_char(FinancialRecord.date, "YYYY-MM").label("month"),
        func.coalesce(func.sum(case((FinancialRecord.type == RecordType.income, FinancialRecord.amount), else_=0)), 0).label("income"),
        func.coalesce(func.sum(case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount), else_=0)), 0).label("expenses")
    ).filter(
        FinancialRecord.deleted_at == None
    ).group_by("month").order_by("month").all()

    return {"data": [
        {
            "month": r.month,
            "income": float(r.income),
            "expenses": float(r.expenses),
            "net": float(r.income) - float(r.expenses)
        } for r in results
    ]}