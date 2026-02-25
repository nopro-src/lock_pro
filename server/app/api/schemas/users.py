from pydantic import BaseModel, EmailStr


class AccountOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool