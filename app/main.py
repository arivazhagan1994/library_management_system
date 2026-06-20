from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import connect_to_mongo, close_mongo_connection
from app.routers.auth import router as auth_router
from app.routers.librarian import router as librarian_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Application Starting")

    await connect_to_mongo()

    print("✅ Startup Complete")

    yield

    print("🛑 Application Shutting Down")

    await close_mongo_connection()

app = FastAPI(
    title="Secure LMS Engine",
    lifespan=lifespan
)

app.include_router(auth_router, prefix="/auth")
app.include_router(librarian_router, prefix="/librarian")

@app.get("/")
async def root():
    return {"message": "Library Management System API Running"}