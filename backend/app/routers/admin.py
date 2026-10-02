from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import student_import, credentials, csv_parser
from app.utils.deps import require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/upload-students")
async def upload_students(
    file: UploadFile = File(...),
    mode: str = Form("skip"),                     # skip | update | abort
    user: dict = Depends(require_role("main_admin")),
    db: Session = Depends(get_db),
):
    if mode not in ("skip", "update", "abort"):
        raise HTTPException(400, "mode must be skip|update|abort")
    raw = await file.read()
    rows, errors = csv_parser.parse_student_csv(raw)
    if not rows and errors:
        raise HTTPException(400, {"errors": errors})
    result = student_import.import_students(db, rows, mode, user["sub"])
    return {
        "total_rows": len(rows),
        "inserted": result["inserted"],
        "updated": result["updated"],
        "skipped": result["skipped"],
        "errors": errors + result["errors"],
        "credentials": result.get("credentials", []),
    }


@router.post("/upload-admins")
async def upload_admins(
    file: UploadFile = File(...),
    user: dict = Depends(require_role("main_admin")),
    db: Session = Depends(get_db),
):
    raw = await file.read()
    rows, errors = csv_parser.parse_admin_csv(raw)
    if not rows and errors:
        raise HTTPException(400, {"errors": errors})
    result = student_import.import_admins(db, rows, user["sub"])
    return {"total_rows": len(rows), **result, "errors": errors + result["errors"]}


@router.get("/credentials/{branch}")
def credentials_branch(
    branch: str,
    user: dict = Depends(require_role("main_admin", "branch_admin")),
    db: Session = Depends(get_db),
):
    if user["role"] == "branch_admin" and user.get("branch") != branch.upper():
        raise HTTPException(403, "Not your branch")
    data = credentials.branch_credentials_csv(db, branch)
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={branch.upper()}_credentials.csv"},
    )


@router.get("/credentials-all")
def credentials_all(
    user: dict = Depends(require_role("main_admin")),
    db: Session = Depends(get_db),
):
    data = credentials.all_branch_credentials_zip(db)
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=credentials_all.zip"},
    )