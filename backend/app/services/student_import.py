from sqlalchemy.orm import Session

from app.models.student import Student
from app.services.audit import write_audit
from app.utils.security import hash_password
from app.services.csv_parser import generate_password

def import_students(
    db: Session,
    rows: list[dict],
    mode: str,
    actor_id: str,
) -> dict:
    """mode: 'skip' | 'update' | 'abort'"""
    inserted = updated = skipped = 0
    created_credentials: list[dict] = []

    if mode == "abort":
        existing = {r["uid"] for r in db.query(Student.uid).all()}
        clashes = [r["uid"] for r in rows if r["uid"] in existing]
        if clashes:
            return {
                "inserted": 0, "updated": 0, "skipped": 0,
                "errors": [f"Aborted. Existing UIDs: {', '.join(clashes[:20])}"],
            }

    for r in rows:
        student = db.query(Student).filter(Student.uid == r["uid"]).first()
        if student:
            if mode == "skip":
                skipped += 1
                continue
            if mode == "update":
                student.name = r["name"]
                student.cgpa = r["cgpa"]
                student.contact_no = r["contact_no"]
                student.parent_branch = r["parent_branch"]
                updated += 1
                continue

        pwd = generate_password()
        db.add(Student(
            uid=r["uid"], name=r["name"], cgpa=r["cgpa"],
            contact_no=r["contact_no"], parent_branch=r["parent_branch"],
            password_hash=hash_password(pwd), must_change_password=True,
        ))
        created_credentials.append({
            "uid": r["uid"], "name": r["name"],
            "branch": r["parent_branch"], "password": pwd,
        })
        inserted += 1

    write_audit(db, actor_id, "main_admin", "csv_upload_students",
                target=f"mode={mode}", new_value=f"inserted={inserted}")
    db.commit()

    return {
        "inserted": inserted, "updated": updated, "skipped": skipped,
        "errors": [], "credentials": created_credentials,
    }


def import_admins(db: Session, rows: list[dict], actor_id: str) -> dict:
    from app.models.admin import Admin

    inserted = skipped = 0
    errors: list[str] = []
    for r in rows:
        exists = db.query(Admin).filter(Admin.admin_id == r["admin_id"]).first()
        if exists:
            skipped += 1
            continue
        db.add(Admin(
            admin_id=r["admin_id"], name=r["name"],
            password_hash=hash_password("changeme123"),
            role="branch_admin", branch=r["branch"],
        ))
        inserted += 1

    write_audit(db, actor_id, "main_admin", "csv_upload_admins",
                new_value=f"inserted={inserted}")
    db.commit()
    return {"inserted": inserted, "skipped": skipped, "errors": errors}