from pydantic import BaseModel
class VerifyIn(BaseModel):
    lock_id: int
    image: str  # base64
    source: str = "web"


class VerifyOut(BaseModel):
    success: bool
    best_account_id: int | None
    score: float
    threshold: float
    engine_key: str