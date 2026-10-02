from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient_uid = Column(String(32), nullable=True, index=True)   # NULL = broadcast
    branch = Column(String(64), nullable=True, index=True)          # scope filter
    title = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)
    created_by = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)