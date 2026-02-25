from pydantic import BaseModel


class EnrollIn(BaseModel):
    lock_id: int
    target_account_id: int
    images: list[str]  # 5 shots base64


class EnrollOut(BaseModel):
    template_id: int
    lock_id: int
    account_id: int
    engine_key: str
    dim: int
    shots: int