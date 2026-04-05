from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import RegisterRequest, LoginRequest, UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, body.name, body.email, body.password, body.role)
    return user

@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.login_user(db, body.email, body.password)
    return {"token": result["token"], "user": UserResponse.model_validate(result["user"])}