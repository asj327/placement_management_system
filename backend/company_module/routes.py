from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import bcrypt
from jose import jwt, JWTError, ExpiredSignatureError
import datetime

from database import get_db
from company_module.schemas import (
    CompanyRegisterModel,
    CompanyLoginModel,
    PostJobModel,
    UpdateStatusModel,
)

router = APIRouter(prefix="/company", tags=["Company"])

SECRET_KEY = "your-secret-key-change-this"   # must match student_routes.py
ALGORITHM = "HS256"


# ─────────────────────────────────────────────────────────
# JWT HELPERS
# ─────────────────────────────────────────────────────────

def generate_token(company_id: int) -> str:
    payload = {
        "company_id": company_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_company(authorization: Optional[str] = Header(None)) -> int:
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")
    try:
        token = authorization.split(" ")[1]
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data["company_id"]
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired, please login again")
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid token")


# ─────────────────────────────────────────────────────────
# ROUTE 1: COMPANY REGISTRATION
# POST /company/register
# ─────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
def register(data: CompanyRegisterModel):
    password_hash = bcrypt.hashpw(
        data.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO companies
                (company_name, email, password_hash, industry, website, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data.company_name,
                data.email,
                password_hash,
                data.industry,
                data.website,
                data.description,
            ),
        )
        conn.commit()
        return {"message": "Company registered successfully!"}

    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=409, detail="Email already registered")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────────────────
# ROUTE 2: COMPANY LOGIN
# POST /company/login
# ─────────────────────────────────────────────────────────

@router.post("/login")
def login(data: CompanyLoginModel):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM companies WHERE email = %s", (data.email,))
        company = cursor.fetchone()

        if not company:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not bcrypt.checkpw(
            data.password.encode("utf-8"),
            company["password_hash"].encode("utf-8"),
        ):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = generate_token(company["company_id"])

        return {
            "message": "Login successful!",
            "token": token,
            "company": {
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "email": company["email"],
                "industry": company["industry"],
                "website": company["website"],
            },
        }

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────────────────
# ROUTE 3: GET COMPANY PROFILE
# GET /company/profile
# ─────────────────────────────────────────────────────────

@router.get("/profile")
def get_profile(company_id: int = Depends(get_current_company)):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT company_id, company_name, email, industry, website, description FROM companies WHERE company_id = %s",
            (company_id,),
        )
        company = cursor.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────────────────
# ROUTE 4: POST A NEW JOB
# POST /company/jobs
# ─────────────────────────────────────────────────────────

@router.post("/jobs", status_code=201)
def post_job(data: PostJobModel, company_id: int = Depends(get_current_company)):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO jobs
                (company_id, job_title, job_type, location, salary,
                 eligibility_cgpa, deadline, job_description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                company_id,
                data.job_title,
                data.job_type,
                data.location,
                data.salary,
                data.eligibility_cgpa,
                data.deadline,
                data.job_description,
            ),
        )
        conn.commit()
        return {"message": "Job posted successfully!", "job_id": cursor.lastrowid}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────────────────
# ROUTE 5: VIEW MY POSTED JOBS
# GET /company/jobs
# ─────────────────────────────────────────────────────────

@router.get("/jobs")
def my_jobs(company_id: int = Depends(get_current_company)):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                job_id, job_title, job_type, location, salary,
                eligibility_cgpa, deadline, job_description,
                CASE WHEN deadline >= CURDATE() THEN 'Active' ELSE 'Expired' END AS status
            FROM jobs
            WHERE company_id = %s
            ORDER BY deadline DESC
            """,
            (company_id,),
        )
        jobs = cursor.fetchall()
        for job in jobs:
            job["salary"] = float(job["salary"]) if job["salary"] else None
            job["eligibility_cgpa"] = float(job["eligibility_cgpa"]) if job["eligibility_cgpa"] else None
            job["deadline"] = str(job["deadline"])
        return {"jobs": jobs, "count": len(jobs)}

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────────────────
# ROUTE 6: DELETE A JOB
# DELETE /company/jobs/{job_id}
# ─────────────────────────────────────────────────────────

@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, company_id: int = Depends(get_current_company)):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verify the job belongs to this company
        cursor.execute(
            "SELECT job_id FROM jobs WHERE job_id = %s AND company_id = %s",
            (job_id, company_id),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job not found or unauthorized")

        cursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
        conn.commit()
        return {"message": "Job deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────────────────
# ROUTE 7: VIEW APPLICANTS FOR MY JOBS
# GET /company/applicants
# Optional: ?job_id=101 to filter by a specific job
# ─────────────────────────────────────────────────────────

@router.get("/applicants")
def view_applicants(
    job_id: Optional[int] = None,
    company_id: int = Depends(get_current_company),
):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT
                a.application_id,
                a.applied_date,
                a.status,
                s.student_id,
                s.first_name,
                s.last_name,
                s.email,
                s.department,
                s.cgpa,
                s.phone,
                j.job_id,
                j.job_title,
                j.job_type
            FROM applications a
            JOIN students s ON a.student_id = s.student_id
            JOIN jobs j ON a.job_id = j.job_id
            WHERE j.company_id = %s
        """
        params = [company_id]

        if job_id:
            query += " AND j.job_id = %s"
            params.append(job_id)

        query += " ORDER BY a.applied_date DESC"

        cursor.execute(query, params)
        applicants = cursor.fetchall()
        for app in applicants:
            app["applied_date"] = str(app["applied_date"])
            app["cgpa"] = float(app["cgpa"]) if app["cgpa"] else None

        return {"applicants": applicants, "count": len(applicants)}

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────────────────
# ROUTE 8: UPDATE APPLICANT STATUS
# PATCH /company/applicants/{application_id}
# ─────────────────────────────────────────────────────────

VALID_STATUSES = {"Pending", "Selected", "Rejected"}

@router.patch("/applicants/{application_id}")
def update_applicant_status(
    application_id: int,
    data: UpdateStatusModel,
    company_id: int = Depends(get_current_company),
):
    if data.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}",
        )

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verify this application belongs to a job owned by this company
        cursor.execute(
            """
            SELECT a.application_id
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            WHERE a.application_id = %s AND j.company_id = %s
            """,
            (application_id, company_id),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Application not found or unauthorized")

        cursor.execute(
            "UPDATE applications SET status = %s WHERE application_id = %s",
            (data.status, application_id),
        )
        conn.commit()
        return {"message": f"Status updated to '{data.status}'"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()