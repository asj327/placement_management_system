from fastapi import APIRouter
from database import get_db

router = APIRouter()

@router.get("/view_applicants")
def view_applicants():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            a.application_id,
            s.first_name,
            s.last_name,
            j.job_title,
            a.status
        FROM applications a
        JOIN students s ON a.student_id = s.student_id
        JOIN jobs j ON a.job_id = j.job_id
        """
        cursor.execute(query)
        result = cursor.fetchall()
        return {"applicants": result}

    finally:
        cursor.close()
        conn.close()