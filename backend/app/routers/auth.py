from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, LookupResponse,
)
from app.services import auth_service
from app.utils.captcha import verify_captcha
from app.utils.rate_limit import limiter, LOGIN_LIMIT, REGISTER_LIMIT
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/lookup/{uid}", response_model=LookupResponse)
def lookup(db: Session = Depends(get_db), uid: str = ""):
    student = auth_service.get_student(db, uid)
    if not student:
        raise HTTPException(status_code=404, detail="UID not found")
    return LookupResponse(
        uid=student.uid,
        name=student.name,
        cgpa=student.cgpa,
        parent_branch=student.parent_branch,
        registered=bool(student.password_hash),
    )


@router.post("/register", response_model=TokenResponse)
@limiter.limit(REGISTER_LIMIT)
async def register(
    request: Request,
    body: RegisterRequest,
    db: Session = Depends(get_db),
):
    if not await verify_captcha(body.captcha_token):
        raise HTTPException(status_code=400, detail="Captcha verification failed")
    try:
        student = auth_service.register_student(db, body.uid, body.password, body.confirm_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token({"sub": student.uid, "role": "student",
                                 "branch": student.parent_branch})
    return TokenResponse(access_token=token, role="student", display_name=student.name)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(LOGIN_LIMIT)
async def login(
    request: Request,
    body: LoginRequest,
    db: Session = Depends(get_db),
):
    if not await verify_captcha(body.captcha_token):
        raise HTTPException(status_code=400, detail="Captcha verification failed")
    try:
        user = auth_service.authenticate(db, body.identifier, body.password, body.role)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    token = create_access_token({
        "sub": user["id"],
        "role": user["role"],
        "branch": user.get("branch"),
    })
    return TokenResponse(access_token=token, role=user["role"], display_name=user["name"])