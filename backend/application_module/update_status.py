from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db

router = APIRouter()

class UpdateStatus(BaseModel):
    application_id: int
    status: str

@router.put("/update_status")
def update_status(data: UpdateStatus):
    conn = get_db()
    cursor = conn.cursor()

    try:
        query = """
        UPDATE applications
        SET status = %s
        WHERE application_id = %s
        """
        cursor.execute(query, (data.status, data.application_id))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Application not found")

        return {"message": "Status updated successfully"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cursor.close()
        conn.close()