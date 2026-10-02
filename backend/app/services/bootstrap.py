from sqlalchemy.orm import Session

from app.config import settings
from app.models.admin import Admin
from app.utils.security import hash_password


def ensure_main_admin(db: Session) -> None:
    existing = db.query(Admin).filter(Admin.admin_id == settings.MAIN_ADMIN_ID).first()
    if existing:
        return
    admin = Admin(
        admin_id=settings.MAIN_ADMIN_ID,
        name=settings.MAIN_ADMIN_NAME,
        password_hash=hash_password(settings.MAIN_ADMIN_PASSWORD),
        role="main_admin",
        branch=None,
    )
    db.add(admin)
    db.commit()