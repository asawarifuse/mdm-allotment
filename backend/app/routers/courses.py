from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.course import Course
from app.schemas.course import CourseOut, CourseSeatInfo

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.id).all()
    out = []
    for c in courses:
        seats = [
            CourseSeatInfo(
                branch=s.branch,
                seats=s.seats,
                filled_seats=s.filled_seats,
                available=s.seats - s.filled_seats,
            )
            for s in c.seats
        ]
        out.append(CourseOut(
            id=c.id,
            course_name=c.course_name,
            branch_name=c.branch_name,
            syllabus_pdf=c.syllabus_pdf,
            total_seats=sum(s.seats for s in seats),
            seats_by_branch=seats,
        ))
    return out