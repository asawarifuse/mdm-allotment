from pydantic import BaseModel


class UploadResult(BaseModel):
    total_rows: int
    inserted: int
    updated: int
    skipped: int
    errors: list[str]


class StudentRow(BaseModel):
    UID: str
    Name: str
    CGPA: float
    Contact: str
    Branch: str