from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import init_db
from student_routes import router as student_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Placement Management System",
    description="Student Backend API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(student_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
