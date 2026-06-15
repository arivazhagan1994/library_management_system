import re
from pydantic import BaseModel, EmailStr, Field, field_validator

class StudentRegister(BaseModel):
    name: str = Field(..., min_length = 2, max_length = 50)
    roll_no: str
    department: str
    phone: str
    email: EmailStr
    password: str = Field(..., min_length = 8)

    @field_validator('phone')
    @classmethod
    def check_phone_format(cls, value: str):
        if not re.fullmatch(r"^[0-9]{10}$", value):
            raise ValueError("Phone numbers must be exactly 10 raw digits.")
        return value
    
    @field_validator('roll_no')
    @classmethod
    def validate_roll_number(cls, value: str):
        # Using Option 1: Must be exactly the word GUVIDS + 4 digits
        if not re.fullmatch(r"GUVIDS[0-9]{4}", value):
            raise ValueError("Roll number must start with 'GUVIDS' followed by 4 digits (e.g., GUVIDS1234).")
        return value

