from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class HackathonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    link: HttpUrl
    domain: Optional[str] = None
    deadline: Optional[datetime] = None
    is_active: bool = True


class HackathonResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    link: HttpUrl
    domain: Optional[str]
    deadline: Optional[datetime]
    is_active: bool
    created_by_college_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class HackathonRegistrationCreate(BaseModel):
    link_submission: Optional[HttpUrl] = None
    notes: Optional[str] = None


class HackathonRegistrationResponse(BaseModel):
    id: str
    hackathon_id: str
    student_college_id: str
    link_submission: Optional[HttpUrl]
    notes: Optional[str]
    status: str
    acknowledged_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
