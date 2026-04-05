from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timezone
from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.record import FinancialRecord
from app.models.user import User
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse

router = APIRouter(prefix="/records", tags=["Records"])

# list all records, supports filtering and pagination
@router.get("/")
def list_records(
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # only fetch records that havent been deleted
    q = db.query(FinancialRecord).filter(FinancialRecord.deleted_at == None)

    if type:
        q = q.filter(FinancialRecord.type == type)
    if category:
        q = q.filter(FinancialRecord.category.ilike(f"%{category}%"))
    if from_date:
        q = q.filter(FinancialRecord.date >= from_date)
    if to_date:
        q = q.filter(FinancialRecord.date <= to_date)
    if search:
        # search in both notes and category
        q = q.filter(
            FinancialRecord.notes.ilike(f"%{search}%") |
            FinancialRecord.category.ilike(f"%{search}%")
        )

    total = q.count()
    records = q.order_by(FinancialRecord.date.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "data": records,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }

@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.deleted_at == None
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    return record

# only admins can create records
@router.post("/", response_model=RecordResponse, status_code=201)
def create_record(
    body: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    record = FinancialRecord(**body.model_dump(), created_by=current_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.patch("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    body: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.deleted_at == None
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record

# soft delete - just sets deleted_at, doesnt actually remove from db
@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.deleted_at == None
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    record.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Record deleted successfully."}