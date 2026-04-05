from sqlalchemy.orm import Session
from app.models.user import User, UserStatus
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import bcrypt
import os

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")

def register_user(db: Session, name: str, email: str, password: str, role: str):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")
    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role=role,
        status=UserStatus.active
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if user.status == UserStatus.inactive:
        raise HTTPException(status_code=403, detail="Account is deactivated.")
    token = create_token({"id": user.id, "email": user.email, "role": str(user.role.value)})
    return {"token": token, "user": user}