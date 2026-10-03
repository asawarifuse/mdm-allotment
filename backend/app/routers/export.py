from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import export as export_service
from app.utils.deps import require_role

router = APIRouter(prefix="/admin/export", tags=["export"])


@router.get("/excel")
def excel(
    user: dict = Depends(require_role("main_admin")),
    db: Session = Depends(get_db),
):
    data = export_service.export_excel(db)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=allotments.xlsx"},
    )


@router.get("/pdf")
def pdf(
    user: dict = Depends(require_role("main_admin")),
    db: Session = Depends(get_db),
):
    data = export_service.export_pdf(db)
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=allotments.pdf"},
    )