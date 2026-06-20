from fastapi import APIRouter, HTTPException, status
from pydantic import Field, field_validator, BaseModel
from app.database import get_collection
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

router = APIRouter(prefix="/librarian", tags=["Librarian Operations"])
IST = ZoneInfo("Asia/Kolkata")

# --- DATA BLUEPRINTS (SCHEMAS) ---
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
    
# Fixed Indentation: Now a standalone structural validation model
class BookIssue(BaseModel):
    isbn: str
    student_phone: str

    @field_validator('student_phone')
    @classmethod
    def validate_phone(cls, value: str):
        if not re.fullmatch(r"^[0-9]{10}$", value):
            raise ValueError("Student phone must be exactly 10 digits.")
        return value


# --- CORE OPERATIONAL ENDPOINTS ---

@router.post("/books", status_code=status.HTTP_201_CREATED)
async def add_new_book(book_data: BookCreate):
    # Localized collection access
    books_collection = get_collection("books")
    
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
    # Localized collection access
    books_collection = get_collection("books")
    
    cursor = books_collection.find({}, {"_id": 0})
    books_list = await cursor.to_list(length=100)  
    return {"total_available": len(books_list), "books": books_list}

@router.post("/issue")
async def issue_book_to_student(payload: BookIssue):
    # Localized collection access
    books_collection = get_collection("books")
    issued_collection = get_collection("issued_books")
    students_collection = get_collection("students")

    book = await books_collection.find_one({"isbn": payload.isbn})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found in available library stock.")
    
    student = await students_collection.find_one({"Phone": payload.student_phone})
    if not student:
        raise HTTPException(status_code=404, detail="Student is not registered in the system.")
    
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
        "renewal_count": 0
    }
    
    await issued_collection.insert_one(loan_record)
    await books_collection.delete_one({"isbn": payload.isbn})
    return {"message": "Book issued successfully!", "due_date": due_date.strftime("%Y-%m-%d")}

@router.post("/return")
async def process_book_return(isbn: str):
    # Localized collection access
    books_collection = get_collection("books")
    issued_collection = get_collection("issued_books")

    loan = await issued_collection.find_one({"isbn": isbn})
    if not loan:
        raise HTTPException(status_code=404, detail="No active loan found tracking this ISBN.")
    
    return_date = datetime.now(IST)
    due_date = loan["due_date"].replace(tzinfo=IST)
    
    current_date_only = return_date.date()
    due_date_only = due_date.date()
    
    penalty_charge = 0
    days_late = 0
    
    if current_date_only > due_date_only:
        date_difference = current_date_only - due_date_only
        days_late = date_difference.days
        penalty_charge = days_late * 20  # ₹20 fine per late day
        
    returned_book = {
        "title": loan["title"],
        "author": loan["author"],
        "isbn": loan["isbn"],
        "restocked_at": return_date
    }
    
    await books_collection.insert_one(returned_book)
    await issued_collection.delete_one({"isbn": isbn})
    
    return {
        "message": f"Book '{loan['title']}' safely returned.",
        "status": "Overdue" if days_late > 0 else "On Time",
        "days_late": days_late,
        "penalty_amount_rupees": penalty_charge
    }

@router.get("/active-loans")
async def view_active_loans():
    # Localized collection access
    issued_collection = get_collection("issued_books")
    
    cursor = issued_collection.find({}, {"_id": 0})
    active_loans = await cursor.to_list(length=100)
    return {"total_active_loans": len(active_loans), "loans": active_loans}