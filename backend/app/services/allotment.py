"""
Formal specification
--------------------
Given:
  S = set of students (uid, cgpa, parent_branch)
  C = set of courses
  B = set of branches
  Q(c, b) = seat quota for course c and branch b
  P(s) = ordered list of 6 course preferences for student s

Allotment is a function A: S -> C defined as:
  Sort S in descending order of (cgpa, earlier submitted_at as tiebreak).
  For each s in sorted order:
    For k = 1..6:
      c = P(s)[k]
      if |{s' in S : A(s') = c and branch(s') = branch(s)}| < Q(c, branch(s)):
        A(s) = c ; break
    If no k matched, find any c with an open seat for branch(s).
    If none exists, s is unallotted (should not happen given quotas sum ≥ |S|).

Complexity: O(N log N + N*K) where N = |S|, K = 6.
"""

import hashlib
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.allotment import Allotment
from app.models.course import CourseSeat
from app.models.preference import Preference
from app.models.student import Student
from app.services.audit import write_audit


def _sort_key(row):
    """Descending CGPA, then earlier preference submission (tiebreak)."""
    uid, cgpa, submitted_at = row
    ts = submitted_at.timestamp() if submitted_at else float("inf")
    return (-cgpa, ts)


def run_allotment(db: Session, actor_id: str, actor_role: str,
                  course_id: int | None = None) -> dict:
    """If course_id is None, runs college-wide. Otherwise runs for one course
    (faculty-scoped, other courses untouched)."""

    # 1. Clear prior allotments in scope
    if course_id is None:
        db.query(Allotment).delete()
        db.query(CourseSeat).update({CourseSeat.filled_seats: 0})
    else:
        db.query(Allotment).filter(Allotment.course_id == course_id).delete()
        db.query(CourseSeat).filter(CourseSeat.course_id == course_id).update(
            {CourseSeat.filled_seats: 0}
        )
    db.flush()

    # 2. Lock seat rows (SELECT FOR UPDATE where supported)
    seat_rows = (
        db.query(CourseSeat)
        .filter(CourseSeat.course_id == course_id if course_id else True)
        .with_for_update()
        .all()
    )
    seat_map: dict[tuple[int, str], CourseSeat] = {
        (s.course_id, s.branch): s for s in seat_rows
    }

    # 3. Load students + their preferences (with submission timestamp)
    prefs_all = (
        db.query(Preference.student_uid,
                 Preference.course_id,
                 Preference.rank,
                 Preference.submitted_at)
        .order_by(Preference.student_uid, Preference.rank)
        .all()
    )
    prefs_by_uid: dict[str, list[tuple[int, datetime]]] = {}
    earliest_submit: dict[str, datetime] = {}
    for uid, cid, rank, ts in prefs_all:
        prefs_by_uid.setdefault(uid, []).append((cid, rank))
        if uid not in earliest_submit or ts < earliest_submit[uid]:
            earliest_submit[uid] = ts

    students = db.query(Student).all()
    ordered = sorted(
        [(s.uid, s.cgpa, s.parent_branch, earliest_submit.get(s.uid))
         for s in students if s.uid in prefs_by_uid],
        key=lambda r: (-r[1], r[3].timestamp() if r[3] else float("inf"))
    )

    # 4. Allot
    allotted = 0
    unallotted: list[str] = []
    results: list[dict] = []

    for uid, cgpa, branch, _ in ordered:
        prefs = prefs_by_uid[uid]
        chosen_course = None
        chosen_rank = None

        # preference scan
        for cid, rank in prefs:
            if course_id is not None and cid != course_id:
                continue
            seat = seat_map.get((cid, branch))
            if seat and seat.filled_seats < seat.seats:
                chosen_course = cid
                chosen_rank = rank
                seat.filled_seats += 1
                break

        # fallback to any open seat
        if chosen_course is None:
            for (cid, b), seat in seat_map.items():
                if b == branch and seat.filled_seats < seat.seats:
                    if course_id is not None and cid != course_id:
                        continue
                    chosen_course = cid
                    chosen_rank = None
                    seat.filled_seats += 1
                    break

        if chosen_course is None:
            unallotted.append(uid)
            continue

        db.add(Allotment(
            student_uid=uid,
            course_id=chosen_course,
            branch=branch,
            choice_number=chosen_rank,
        ))
        allotted += 1
        results.append({"uid": uid, "course_id": chosen_course, "rank": chosen_rank})

    # 5. Audit + summary
    scope = f"course={course_id}" if course_id else "college-wide"
    write_audit(db, actor_id, actor_role, "run_allotment",
                target=scope,
                new_value=f"allotted={allotted},unallotted={len(unallotted)}")
    db.commit()

    return {
        "scope": scope,
        "allotted": allotted,
        "unallotted": unallotted,
        "results": results[:50],  # truncated preview
    }