from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
import bcrypt
from jose import jwt, JWTError, ExpiredSignatureError
import datetime
from db import get_connection

router = APIRouter(prefix="/student", tags=["Student"])

SECRET_KEY = 'your-secret-key-change-this'
ALGORITHM = 'HS256'


# ─────────────────────────────────────────────
# PYDANTIC MODELS (request body validation)
# ─────────────────────────────────────────────

class RegisterModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    department: str
    cgpa: float
    phone: Optional[str] = None

class LoginModel(BaseModel):
    email: str
    password: str

class ApplyModel(BaseModel):
    job_id: int


# ─────────────────────────────────────────────
# JWT HELPERS
# ─────────────────────────────────────────────

def generate_token(student_id: int) -> str:
    payload = {
        'student_id': student_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_student(authorization: Optional[str] = Header(None)) -> int:
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")
    try:
        token = authorization.split(" ")[1]
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data['student_id']
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired, please login again")
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid token")


# ─────────────────────────────────────────────
# ROUTE 1: STUDENT REGISTRATION
# POST /student/register
# ─────────────────────────────────────────────

@router.post("/register", status_code=201)
def register(data: RegisterModel):

    if not (0 <= data.cgpa <= 10):
        raise HTTPException(status_code=400, detail="CGPA must be between 0 and 10")

    password_hash = bcrypt.hashpw(
        data.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO students
                (first_name, last_name, email, password_hash, department, cgpa, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            data.first_name,
            data.last_name,
            data.email,
            password_hash,
            data.department,
            data.cgpa,
            data.phone
        ))
        conn.commit()
        return {"message": "Registration successful!"}

    except Exception as e:
        if 'Duplicate entry' in str(e):
            raise HTTPException(status_code=409, detail="Email already registered")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# ROUTE 2: STUDENT LOGIN
# POST /student/login
# ─────────────────────────────────────────────

@router.post("/login")
def login(data: LoginModel):

    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM students WHERE email = %s', (data.email,))
        student = cursor.fetchone()

        if not student:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        password_matches = bcrypt.checkpw(
            data.password.encode('utf-8'),
            student['password_hash'].encode('utf-8')
        )

        if not password_matches:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = generate_token(student['student_id'])

        return {
            "message": "Login successful!",
            "token": token,
            "student": {
                "student_id": student['student_id'],
                "name": f"{student['first_name']} {student['last_name']}",
                "email": student['email'],
                "department": student['department'],
                "cgpa": float(student['cgpa'])
            }
        }

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# ROUTE 3: VIEW JOBS
# GET /student/jobs
# Optional query param: ?type=Internship
# ─────────────────────────────────────────────

@router.get("/jobs")
def view_jobs(
    type: Optional[str] = None,
    student_id: int = Depends(get_current_student)
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT cgpa FROM students WHERE student_id = %s', (student_id,))
        student = cursor.fetchone()
        student_cgpa = float(student['cgpa'])

        query = '''
            SELECT
                j.job_id,
                j.job_title,
                j.location,
                j.salary,
                j.eligibility_cgpa,
                j.job_type,
                j.deadline,
                j.job_description,
                c.company_name,
                c.website
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            WHERE j.deadline >= CURDATE()
              AND (j.eligibility_cgpa IS NULL OR j.eligibility_cgpa <= %s)
        '''
        params = [student_cgpa]

        if type:
            query += ' AND j.job_type = %s'
            params.append(type)

        query += ' ORDER BY j.deadline ASC'

        cursor.execute(query, params)
        jobs = cursor.fetchall()

        for job in jobs:
            job['salary'] = float(job['salary']) if job['salary'] else None
            job['eligibility_cgpa'] = float(job['eligibility_cgpa']) if job['eligibility_cgpa'] else None
            job['deadline'] = str(job['deadline'])

        return {"jobs": jobs, "count": len(jobs)}

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# ROUTE 4: APPLY FOR A JOB
# POST /student/apply
# ─────────────────────────────────────────────

@router.post("/apply", status_code=201)
def apply_job(
    data: ApplyModel,
    student_id: int = Depends(get_current_student)
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT * FROM jobs WHERE job_id = %s AND deadline >= CURDATE()',
            (data.job_id,)
        )
        job = cursor.fetchone()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found or deadline has passed")

        cursor.execute('SELECT cgpa FROM students WHERE student_id = %s', (student_id,))
        student = cursor.fetchone()
        if job['eligibility_cgpa'] and float(student['cgpa']) < float(job['eligibility_cgpa']):
            raise HTTPException(status_code=403, detail="You do not meet the CGPA requirement for this job")

        cursor.execute('''
            INSERT INTO applications (student_id, job_id)
            VALUES (%s, %s)
        ''', (student_id, data.job_id))
        conn.commit()

        return {"message": "Application submitted successfully!"}

    except HTTPException:
        raise
    except Exception as e:
        if 'Duplicate entry' in str(e):
            raise HTTPException(status_code=409, detail="You have already applied for this job")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# BONUS: VIEW MY APPLICATIONS
# GET /student/my-applications
# ─────────────────────────────────────────────

@router.get("/my-applications")
def my_applications(student_id: int = Depends(get_current_student)):

    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT
                a.application_id,
                a.applied_date,
                a.status,
                j.job_title,
                j.job_type,
                j.location,
                j.salary,
                c.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            WHERE a.student_id = %s
            ORDER BY a.applied_date DESC
        ''', (student_id,))

        applications = cursor.fetchall()
        for app in applications:
            app['salary'] = float(app['salary']) if app['salary'] else None
            app['applied_date'] = str(app['applied_date'])

        return {"applications": applications}

    finally:
        cursor.close()
        conn.close()
