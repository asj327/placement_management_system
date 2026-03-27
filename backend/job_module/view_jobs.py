from fastapi import APIRouter
from database import get_db

router = APIRouter()

@router.get("/view_jobs")
def view_jobs():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM jobs")
        jobs = cursor.fetchall()
        return {"jobs": jobs}

    finally:
        cursor.close()
        conn.close()