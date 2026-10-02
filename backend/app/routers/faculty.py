from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.faculty import FacultyCourseInfo, SeatUpdate
from app.services import faculty as faculty_service
from app.utils.deps import require_role

router = APIRouter(prefix="/faculty", tags=["faculty"])


@router.get("/dashboard", response_model=FacultyCourseInfo)
def dashboard(
    user: dict = Depends(require_role("branch_admin", "main_admin")),
    db: Session = Depends(get_db),
):
    branch = user.get("branch")
    if not branch:
        raise HTTPException(400, "No branch assigned to this admin")

    course = faculty_service.get_faculty_course(db, branch)
    if not course:
        raise HTTPException(404, f"No course offered by branch {branch}")

    return FacultyCourseInfo(
        course_id=course.id,
        course_name=course.course_name,
        branch_name=course.branch_name,
        students_selected=faculty_service.get_students_who_selected(db, course.id),
        seats_by_branch=faculty_service.get_seats(db, course.id),
    )


@router.put("/seats")
def update_seat(
    body: SeatUpdate,
    user: dict = Depends(require_role("branch_admin")),
    db: Session = Depends(get_db),
):
    branch = user.get("branch")
    if not branch:
        raise HTTPException(400, "No branch assigned")
    course = faculty_service.get_faculty_course(db, branch)
    if not course:
        raise HTTPException(404, "No course for your branch")

    try:
        return faculty_service.update_seat(db, course.id, body.branch, body.seats, user["sub"])
    except ValueError as e:
        raise HTTPException(400, str(e))