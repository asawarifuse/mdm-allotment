from pydantic import BaseModel, Field, field_validator


class PreferenceSubmit(BaseModel):
    course_ids: list[int] = Field(min_length=6, max_length=6)

    @field_validator("course_ids")
    @classmethod
    def no_duplicates(cls, v):
        if len(set(v)) != len(v):
            raise ValueError("Duplicate courses not allowed")
        return v


class PreferenceOut(BaseModel):
    rank: int
    course_id: int
    course_name: str
    branch_name: str


class PreferenceStatus(BaseModel):
    submitted: bool
    submitted_at: str | None
    preferences: list[PreferenceOut]