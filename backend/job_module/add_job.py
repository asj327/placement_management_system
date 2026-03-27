from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db

router = APIRouter()

class Job(BaseModel):
    company_id: int
    job_title: str
    job_description: str
    location: str = None
    salary: float = None
    eligibility_cgpa: float = None
    job_type: str = "Full-Time"
    deadline: str

@router.post("/add_job")
def add_job(job: Job):
    conn = get_db()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO jobs
        (company_id, job_title, job_description, location, salary, eligibility_cgpa, job_type, deadline)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            job.company_id,
            job.job_title,
            job.job_description,
            job.location,
            job.salary,
            job.eligibility_cgpa,
            job.job_type,
            job.deadline
        )
        cursor.execute(query, values)
        conn.commit()

        return {"message": "Job added successfully"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cursor.close()
        conn.close()