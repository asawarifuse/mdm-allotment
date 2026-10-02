from sqlalchemy import Column, String, DateTime, func
from app.database import Base


class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(String(32), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(16), nullable=False)          # "main_admin" | "branch_admin"
    branch = Column(String(64), nullable=True, index=True)  # NULL for main_admin
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)