from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.database import get_db
from app.models.user import User, UserStatus
import os

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        user_id = payload.get("id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    if user.status == UserStatus.inactive:
        raise HTTPException(status_code=403, detail="Account is deactivated.")
    return user

def require_role(*roles):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {' or '.join(roles)}."
            )
        return current_user
    return checker

# Convenience shortcuts
def require_admin(current_user: User = Depends(get_current_user)):
    return require_role("admin")(current_user)

def require_analyst_or_above(current_user: User = Depends(get_current_user)):
    return require_role("analyst", "admin")(current_user)

def require_any_role(current_user: User = Depends(get_current_user)):
    return current_user

# this runs on every protected route to check the token