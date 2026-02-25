from pydantic import BaseModel


class SystemInfoOut(BaseModel):
    engine_key: str
    threshold: float
    enroll_shots: int