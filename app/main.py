# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, librarian

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # 1. Boot up the asynchronous MongoDB client connection pool
    await connect_to_mongo()
    
    # 🔍 ZERO-MATH ZERO-BIAS PATH INSPECTOR (Reads literal routing keys)
    print("\n🗺️ --- ABSOLUTE REALITY ROUTE MAP ---")
    for route in app.routes:
        if hasattr(route, "path"):
            methods = ",".join(route.methods) if hasattr(route, "methods") else "ANY"
            print(f" 👉 Path: {route.path} [{methods}]")
        elif hasattr(route, "routes"):
            for sub_route in route.routes:
                sub_methods = ",".join(sub_route.methods) if hasattr(sub_route, "methods") else "ANY"
                print(f" 👉 Path: {sub_route.path} [{sub_methods}]")
    print("--------------------------------------\n")
    
    yield
    # 2. Terminate database streams cleanly on server shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Secure LMS Engine", 
    lifespan=app_lifespan
)

# Connect routers plainly with absolute paths handled inside the files
app.include_router(auth.router)
app.include_router(librarian.router)