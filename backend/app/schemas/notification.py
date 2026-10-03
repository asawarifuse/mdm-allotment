from pydantic import BaseModel


class NotificationCreate(BaseModel):
    recipient_uid: str | None = None
    branch: str | None = None
    title: str
    message: str


class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    branch: str | None
    created_by: str
    created_at: str
    read: bool