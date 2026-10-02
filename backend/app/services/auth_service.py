from sqlalchemy.orm import Session

from app.models.admin import Admin
from app.models.student import Student
from app.services.audit import write_audit
from app.utils.security import hash_password, verify_password


def get_student(db: Session, uid: str) -> Student | None:
    return db.query(Student).filter(Student.uid == uid.upper()).first()


def get_admin(db: Session, admin_id: str) -> Admin | None:
    return db.query(Admin).filter(Admin.admin_id == admin_id).first()


def register_student(db: Session, uid: str, password: str, confirm_password: str) -> Student:
    uid = uid.strip().upper()
    if password != confirm_password:
        raise ValueError("Passwords do not match")

    student = get_student(db, uid)
    if not student:
        raise ValueError("UID not found in roster. Contact your branch admin.")
    if student.password_hash:
        raise ValueError("UID already registered. Please login.")

    student.password_hash = hash_password(password)
    student.must_change_password = False
    write_audit(db, uid, "student", "register", target=uid)
    db.commit()
    db.refresh(student)
    return student


def authenticate(db: Session, identifier: str, password: str, role: str):
    if role == "student":
        student = get_student(db, identifier)
        if not student or not student.password_hash:
            raise ValueError("Invalid credentials")
        if not verify_password(password, student.password_hash):
            raise ValueError("Invalid credentials")
        return {"id": student.uid, "role": "student", "name": student.name,
                "branch": student.parent_branch, "must_change": student.must_change_password}

    if role in ("branch_admin", "main_admin"):
        admin = get_admin(db, identifier)
        if not admin or not verify_password(password, admin.password_hash):
            raise ValueError("Invalid credentials")
        if admin.role != role:
            raise ValueError("Invalid credentials")
        return {"id": admin.admin_id, "role": admin.role, "name": admin.name,
                "branch": admin.branch, "must_change": False}

    raise ValueError("Invalid role")