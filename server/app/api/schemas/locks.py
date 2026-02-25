from pydantic import BaseModel


class LockCreateIn(BaseModel):
    name: str


class LockOut(BaseModel):
    id: int
    name: str
    code: str


class AddMemberIn(BaseModel):
    email: str
    role: str  # OWNER | USER


class MemberOut(BaseModel):
    account_id: int
    role: str