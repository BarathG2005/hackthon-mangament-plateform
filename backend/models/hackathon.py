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
    source: str = "manual"
    suggested_by_model: Optional[str] = None


class HackathonAISuggest(BaseModel):
    title: str
    description: Optional[str] = None
    link: HttpUrl
    domain: Optional[str] = None
    deadline: Optional[datetime] = None
    suggested_by_model: Optional[str] = None


class HackathonResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    link: HttpUrl
    domain: Optional[str] = None
    deadline: Optional[datetime] = None
    is_active: bool
    approval_status: str
    approved_by: Optional[str] = None
    source: Optional[str] = None
    suggested_by_model: Optional[str] = None
    created_by_college_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


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


class HackathonDepartmentStats(BaseModel):
    department: Optional[str]
    registered: int
    remaining: int
    total_students: int


class HackathonStatsResponse(BaseModel):
    hackathon_id: str
    title: Optional[str]
    total_registered: int
    per_department: List[HackathonDepartmentStats]
    last_updated: datetime
