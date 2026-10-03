from sqlalchemy.orm import Session

from app.models.allotment import Allotment
from app.models.course import Course, CourseSeat


def get_seat_matrix(db: Session) -> dict:
    courses = db.query(Course).order_by(Course.id).all()
    cells = (
        db.query(CourseSeat)
        .order_by(CourseSeat.course_id, CourseSeat.branch)
        .all()
    )
    branches = sorted({c.branch for c in cells})
    course_rows = [
        {"course_id": c.id, "course_name": c.course_name, "offering_branch": c.branch_name}
        for c in courses
    ]
    course_names = {c.id: c.course_name for c in courses}
    cell_list = [
        {
            "course_id": s.course_id,
            "course_name": course_names.get(s.course_id, ""),
            "branch": s.branch,
            "seats": s.seats,
            "filled_seats": s.filled_seats,
            "available": s.seats - s.filled_seats,
        }
        for s in cells
    ]
    return {"branches": branches, "courses": course_rows, "cells": cell_list}


def get_master_allotments(db: Session) -> list[dict]:
    rows = (
        db.query(Allotment, Course)
        .join(Course, Course.id == Allotment.course_id)
        .order_by(Allotment.branch, Allotment.student_uid)
        .all()
    )
    from app.models.student import Student
    uids = [a.student_uid for a, _ in rows]
    students = {s.uid: s for s in db.query(Student).filter(Student.uid.in_(uids)).all()}

    out = []
    for a, c in rows:
        s = students.get(a.student_uid)
        if not s:
            continue
        out.append({
            "uid": s.uid,
            "name": s.name,
            "cgpa": s.cgpa,
            "parent_branch": s.parent_branch,
            "course_id": c.id,
            "course_name": c.course_name,
            "offering_branch": c.branch_name,
            "choice_number": a.choice_number,
            "allotted_at": a.allotted_at.isoformat() if a.allotted_at else "",
        })
    return out