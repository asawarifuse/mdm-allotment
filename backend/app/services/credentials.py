import csv
import io
import zipfile

from sqlalchemy.orm import Session

from app.models.student import Student


def branch_credentials_csv(db: Session, branch: str) -> bytes:
    students = (
        db.query(Student)
        .filter(Student.parent_branch == branch.upper())
        .order_by(Student.uid)
        .all()
    )
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["UID", "Name", "Branch", "Note"])
    for s in students:
        w.writerow([s.uid, s.name, s.parent_branch,
                    "Password issued at upload. Ask admin to reset if lost."])
    return buf.getvalue().encode("utf-8")


def all_branch_credentials_zip(db: Session) -> bytes:
    branches = [b[0] for b in db.query(Student.parent_branch).distinct().all()]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for b in branches:
            z.writestr(f"{b}_credentials.csv", branch_credentials_csv(db, b))
    return buf.getvalue()