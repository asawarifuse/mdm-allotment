from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_name = Column(String(64), nullable=False)      # offering department
    course_name = Column(String(128), nullable=False)
    syllabus_pdf = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    seats = relationship("CourseSeat", back_populates="course", cascade="all, delete-orphan")


class CourseSeat(Base):
    __tablename__ = "course_seats"
    __table_args__ = (UniqueConstraint("course_id", "branch", name="uq_course_branch"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    branch = Column(String(64), nullable=False, index=True)   # student's parent branch
    seats = Column(Integer, nullable=False, default=5)
    filled_seats = Column(Integer, nullable=False, default=0)

    course = relationship("Course", back_populates="seats")