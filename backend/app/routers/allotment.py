from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.allotment import AllotmentRunResponse
from app.services import allotment as allotment_service
from app.services import faculty as faculty_service
from app.utils.deps import require_role

router = APIRouter(prefix="/allotment", tags=["allotment"])


@router.post("/run/college", response_model=AllotmentRunResponse)
def run_college(
    user: dict = Depends(require_role("main_admin")),
    db: Session = Depends(get_db),
):
    return allotment_service.run_allotment(db, user["sub"], "main_admin", course_id=None)


@router.post("/run/course", response_model=AllotmentRunResponse)
def run_course(
    user: dict = Depends(require_role("branch_admin")),
    db: Session = Depends(get_db),
):
    branch = user.get("branch")
    if not branch:
        raise HTTPException(400, "No branch assigned")
    course = faculty_service.get_faculty_course(db, branch)
    if not course:
        raise HTTPException(404, "No course for your branch")
    return allotment_service.run_allotment(db, user["sub"], "branch_admin", course_id=course.id)