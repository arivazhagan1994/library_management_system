from fastapi import APIRouter, HTTPException, status
from pydantic import Field, field_validator, BaseModel
from app.database import get_collection
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

IST = ZoneInfo("Asia/Kolkata")

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author:str = Field(..., min_length=2, max_length=80)
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

router = APIRouter(prefix="/librarian", tags=["Librarian Operations"])

books_collection = get_collection("books")
issued_collection = get_collection("issued_books")
students_collection = get_collection("students")

@router.post("/books", status_code=status.HTTP_201_CREATED)
async def add_new_book(book_data: BookCreate):
    existing_book = await books_collection.find_one({"isbn": book_data.isbn})
    if existing_book:
        raise HTTPException(status_code=400, detail="A book with this ISBN already exists in stock.")
    
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
    cursor = books_collection.find({}, {"_id": 0})
    books_list = await cursor.to_list(length=100)  
    return {"total_available": len(books_list), "books": books_list}
