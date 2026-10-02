from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey,
    Integer, String, UniqueConstraint, func,
)
from app.database import Base


class Preference(Base):
    __tablename__ = "preferences"
    __table_args__ = (
        UniqueConstraint("student_uid", "rank", name="uq_student_rank"),
        UniqueConstraint("student_uid", "course_id", name="uq_student_course"),
        CheckConstraint("rank >= 1 AND rank <= 6", name="ck_rank_range"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_uid = Column(String(32), ForeignKey("students.uid", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    rank = Column(Integer, nullable=False)  # 1..6
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)