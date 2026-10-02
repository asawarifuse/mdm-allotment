from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.database import Base


class Allotment(Base):
    __tablename__ = "allotments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_uid = Column(String(32), ForeignKey("students.uid", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    branch = Column(String(64), nullable=False, index=True)      # student's parent_branch at allotment time
    choice_number = Column(Integer, nullable=True)               # 1..5, or NULL for fallback
    allotted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)