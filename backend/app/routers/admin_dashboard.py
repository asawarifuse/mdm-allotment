from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.course import CourseSeat
from app.schemas.admin import (
    SeatMatrixResponse, MasterAllotmentRow, ExperimentResponse,
)
from app.services import admin_dashboard, fairness
from app.services.audit import write_audit
from app.utils.deps import require_role

router = APIRouter(prefix="/admin", tags=["admin-dashboard"])


@router.get("/seat-matrix", response_model=SeatMatrixResponse)
def seat_matrix(
    user: dict = Depends(require_role("main_admin")),
    db: Session = Depends(get_db),
):
    return admin_dashboard.get_seat_matrix(db)


@router.put("/seats/{course_id}/{branch}")
def update_seat(
    course_id: int,
    branch: str,
    seats: int,
    user: dict = Depends(require_role("main_admin")),
    db: Session = Depends(get_db),
):
    if seats < 0:
        raise HTTPException(400, "Seats cannot be negative")
    row = (
        db.query(CourseSeat)
        .filter(CourseSeat.course_id == course_id, CourseSeat.branch == branch.upper())
        .first()
    )
    if not row:
        raise HTTPException(404, "Seat row not found")
    if row.filled_seats > 0:
        raise HTTPException(400, "Cannot edit seats after allotment")
    old = row.seats
    row.seats = seats
    write_audit(db, user["sub"], "main_admin", "edit_seats",
                target=f"course={course_id},branch={branch}",
                old_value=old, new_value=seats)
    db.commit()
    return {"course_id": course_id, "branch": branch.upper(), "seats": seats, "old": old}


@router.get("/allotments", response_model=list[MasterAllotmentRow])
def master_allotments(
    user: dict = Depends(require_role("main_admin")),
    db: Session = Depends(get_db),
):
    return admin_dashboard.get_master_allotments(db)


@router.post("/experiment/fairness", response_model=ExperimentResponse)
def run_fairness(
    seed: int = 42,
    user: dict = Depends(require_role("main_admin")),
    db: Session = Depends(get_db),
):
    result = fairness.run_fairness_experiment(db, seed=seed)
    write_audit(db, user["sub"], "main_admin", "run_experiment",
                target="fairness", new_value=f"seed={seed}")
    db.commit()
    return result