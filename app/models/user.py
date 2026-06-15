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

