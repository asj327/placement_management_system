from pydantic import BaseModel, EmailStr
from typing import Optional


# ─── AUTH ───────────────────────────────────────────────
class CompanyRegisterModel(BaseModel):
    company_name: str
    email: str
    password: str
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class CompanyLoginModel(BaseModel):
    email: str
    password: str


# ─── JOB POSTING ────────────────────────────────────────
class PostJobModel(BaseModel):
    job_title: str
    job_type: str = "Full-Time"          # Full-Time | Part-Time | Internship
    location: Optional[str] = None
    salary: Optional[float] = None
    eligibility_cgpa: Optional[float] = None
    deadline: str                         # YYYY-MM-DD
    job_description: Optional[str] = None


# ─── APPLICATION STATUS ──────────────────────────────────
class UpdateStatusModel(BaseModel):
    status: str                           # Pending | Selected | Rejected