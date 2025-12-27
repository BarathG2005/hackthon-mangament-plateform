from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    PRINCIPAL = "principal"
    HOD = "hod"
    TEACHER = "teacher"
    STUDENT = "student"

class CollegeUser(BaseModel):
    college_id: str
    name: str
    email: EmailStr
    role: UserRole
    department: Optional[str] = None
    auth_user_id: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class AddUserRequest(BaseModel):
    college_id: str
    name: str
    email: EmailStr
    role: UserRole
    department: Optional[str] = None

class ActivateAccountRequest(BaseModel):
    college_id: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    college_id: str
    name: str
    email: str
    role: UserRole
    department: Optional[str]
    is_active: bool
    auth_user_id: Optional[str]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
