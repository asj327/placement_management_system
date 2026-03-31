from fastapi import FastAPI

from job_module.add_job import router as add_job_router
from job_module.view_jobs import router as view_jobs_router
from application_module.view_applicants import router as view_applicants_router
from application_module.update_status import router as update_status_router

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Placement Management Backend Running (FastAPI)"}

# Include routers
app.include_router(add_job_router)
app.include_router(view_jobs_router)
app.include_router(view_applicants_router)
app.include_router(update_status_router)