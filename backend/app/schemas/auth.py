from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    uid: str
    password: str = Field(min_length=6)
    confirm_password: str
    captcha_token: str | None = None


class LoginRequest(BaseModel):
    identifier: str
    password: str
    role: str  # "student" | "branch_admin" | "main_admin"
    captcha_token: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    display_name: str


class LookupResponse(BaseModel):
    uid: str
    name: str
    cgpa: float
    parent_branch: str
    registered: bool