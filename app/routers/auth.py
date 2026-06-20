# app/routers/auth.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.database import get_collection
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import random
import re
import jwt
import os

# Clean Initialization: No hidden prefix argument
router = APIRouter(tags=["Secure Gateway"])
IST = ZoneInfo("Asia/Kolkata")

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_secret_key_for_safety")
ALGORITHM = "HS256"

class LibrarianLogin(BaseModel):
    email: EmailStr
    password: str

class OTPRequest(BaseModel):
    identifier: str

    @field_validator('identifier')
    @classmethod
    def clean_identifier(cls, v: str):
        v = v.strip()
        if not (re.fullmatch(r"^[0-9]{10}$", v) or re.fullmatch(r"^GUVIDS[0-9]{4}$", v)):
            raise ValueError("Input must be a valid 10-digit mobile number or GUVIDS roll number.")
        return v

class OTPVerify(BaseModel):
    identifier: str
    otp_code: str = Field(..., min_length=6, max_length=6)

# 🟢 Absolute Explicit URL Path Strings
@router.post("/auth/login/librarian")
async def librarian_login(payload: LibrarianLogin):
    if payload.email == "admin@vathiyar.com" and payload.password == "admin1234":
        token = jwt.encode({"sub": "admin", "role": "librarian"}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "role": "librarian", "name": "Head Librarian"}
    raise HTTPException(status_code=401, detail="Invalid Librarian email or password.")

@router.post("/auth/student/request-otp")
async def request_student_otp(payload: OTPRequest):
    students_col = get_collection("students")
    otp_col = get_collection("otp_cache")

    student = await students_col.find_one({
        "$or": [{"Phone": payload.identifier}, {"Roll No": payload.identifier}]
    })

    if not student:
        raise HTTPException(status_code=404, detail="Student credentials not found in library register.")
    
    generated_otp = str(random.randint(100000, 999999))

    await otp_col.update_one(
        {"identifier": payload.identifier},
        {"$set": {
            "otp": generated_otp,
            "created_at": datetime.now(IST),
            "expire_at": datetime.now(IST) + timedelta(minutes=5)
        }},
        upsert=True
    )

    print(f"\n[SMS GATEWAY MOCK] 🔥 Live Verification OTP: {generated_otp} for student: {payload.identifier}\n")
    return {"message": "OTP generated and transmitted successfully!", "mock_otp": generated_otp}

@router.post("/auth/student/verify-otp")
async def verify_student_otp(payload: OTPVerify):
    students_col = get_collection("students")
    otp_col = get_collection("otp_cache")

    cached_record = await otp_col.find_one({"identifier": payload.identifier})
    
    if not cached_record or cached_record["otp"] != payload.otp_code:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP token.")

    student = await students_col.find_one({
        "$or": [{"Phone": payload.identifier}, {"Roll No": payload.identifier}]
    })

    await otp_col.delete_one({"identifier": payload.identifier})

    token_payload = {
        "sub": student["Roll No"],
        "role": "student",
        "name": student["Name"],
        "exp": datetime.now(IST) + timedelta(days=7)
    }
    encoded_jwt = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": encoded_jwt, "role": "student", "name": student["Name"]}