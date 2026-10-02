from sqlalchemy import Column, String, Float, Boolean, DateTime, func
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    uid = Column(String(32), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    cgpa = Column(Float, nullable=False)
    contact_no = Column(String(20), nullable=False)
    parent_branch = Column(String(64), nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    must_change_password = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)