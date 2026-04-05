from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.viewer

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str

    class Config:
        from_attributes = True