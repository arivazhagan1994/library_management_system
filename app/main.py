# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # 1. This happens when the application starts up
    await connect_to_mongo()
    yield
    # 2. This happens when the application safely shuts down
    await close_mongo_connection()

app = FastAPI(
    title="Secure LMS Engine", 
    lifespan=app_lifespan
)

# Connect your separate router systems cleanly
app.include_router(auth.router)

@app.get("/")
async def health_check():
    # Ultra lightweight check to see if the app is responsive without using memory
    return {"status": "healthy", "engine": "running"}