# app/routers/librarian.py
from fastapi import APIRouter, HTTPException, status
from pydantic import Field, field_validator, BaseModel
from app.database import get_collection
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

# Initialize the router context cleanly
router = APIRouter(tags=["Librarian Operations"])
IST = ZoneInfo("Asia/Kolkata")

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=2, max_length=80)
    isbn: str

    @field_validator('isbn')
    @classmethod
    def validate_isbn_format(cls, value):
        if not re.fullmatch(r"^[0-9]{5}$", value):
            raise ValueError("ISBN must be exactly 5 numeric digits.")
        return value
    
class BookIssue(BaseModel):
    isbn: str
    student_phone: str

    @field_validator('student_phone')
    @classmethod
    def validate_phone(cls, value: str):
        if not re.fullmatch(r"^[0-9]{10}$", value):
            raise ValueError("Student phone must be exactly 10 digits.")
        return value

# --- ENDPOINTS ---
@router.post("/books", status_code=status.HTTP_201_CREATED)
async def add_new_book(book_data: BookCreate):
    books_collection = get_collection("books")
    existing_book = await books_collection.find_one({"isbn": book_data.isbn})
    if existing_book:
        raise HTTPException(status_code=400, detail="A book with this ISBN already exists.")
    
    new_book = {
        "title": book_data.title,
        "author": book_data.author,
        "isbn": book_data.isbn,
        "added_at": datetime.now(IST)
    }
    await books_collection.insert_one(new_book)
    return {"message": f"Successfully stored '{book_data.title}' into inventory!"}

@router.get("/books")
async def view_available_stock():
    books_collection = get_collection("books")
    cursor = books_collection.find({}, {"_id": 0})
    books_list = await cursor.to_list(length=100)  
    return {"total_available": len(books_list), "books": books_list}

@router.post("/issue")
async def issue_book_to_student(payload: BookIssue):
    books_collection = get_collection("books")
    issued_collection = get_collection("issued_books")
    students_collection = get_collection("students")

    book = await books_collection.find_one({"isbn": payload.isbn})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found in library stock.")
    if not book.get("available", True):
        raise HTTPException(
            status_code=400,
            detail="Book is already issued."
        )
    
    student = await students_collection.find_one({"Phone": payload.student_phone})
    if not student:
        raise HTTPException(status_code=404, detail="Student is not registered.")
    existing_loan = await issued_collection.find_one({
        "isbn": payload.isbn,
        "returned": False
    })

    if existing_loan:
        raise HTTPException(
            status_code=400,
            detail="Book already issued."
        )
    
    issue_date = datetime.now(IST)
    due_date = issue_date + timedelta(days=15)
    
    loan_record = {
        "title": book["title"],
        "author": book["author"],
        "isbn": book["isbn"],

        "student_name": student["Name"],
        "student_phone": student["Phone"],

        "issued_date": issue_date,
        "due_date": due_date,

        "returned": False,
        "returned_date": None,

        "renewal_count": 0
    }
    await issued_collection.insert_one(loan_record)
    await books_collection.update_one(
        {"isbn": payload.isbn},
        {
            "$set": {
                "available": False
            }
        }
    )
    return {
        "message": "Book issued successfully!",
        "student": student["Name"],
        "book": book["title"],
        "due_date": due_date.strftime("%Y-%m-%d")
    }