"""认证路由 — 注册、登录、登出、日志."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user, require_admin
from app.middleware.security import check_login_block, record_login_fail, reset_login_fails
from app.models.auth_log import AuthLog
from app.models.user import User
from app.services import auth_service
from app.services.email_service import send_verification, verify_code

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Models ──────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class AuthResponse(BaseModel):
    token: str
    username: str
    role: str


class LogItem(BaseModel):
    id: int
    username: str
    action: str
    ip_address: str | None
    created_at: str


# ── Routes ──────────────────────────────────────────────────


@router.post("/register", response_model=AuthResponse, summary="注册")
async def register(request: RegisterRequest, req: Request, db: Session = Depends(get_db)):
    """注册新用户，成功返回 JWT token."""
    try:
        user = auth_service.register_user(db, request.username, request.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    token = auth_service.create_access_token(user.id, user.token_version)
    # 记录日志
    auth_service.log_auth(db, user.username, "register", req.client.host if req.client else None)
    return {"token": token, "username": user.username, "role": user.role}


@router.post("/login", response_model=AuthResponse, summary="登录")
async def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    """登录，成功返回 JWT token。支持用户名或邮箱登录."""
    username_or_email = request.username
    user = (
        db.query(User)
        .filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        )
        .first()
    )
    ip = req.client.host if req.client else "unknown"
    if check_login_block(ip):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="登录失败次数过多，请15分钟后再试")
    if not user:
        record_login_fail(ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="该账号已注销")
    if not auth_service.verify_password(request.password, user.password_hash):
        record_login_fail(ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = auth_service.create_access_token(user.id, user.token_version)
    reset_login_fails(ip)
    auth_service.log_auth(db, user.username, "login", ip)
    return {"token": token, "username": user.username, "role": user.role}


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., max_length=100)


class ResetPasswordRequest(BaseModel):
    email: str
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)


@router.post("/forgot-password", summary="发送重置密码验证码")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """向已绑定邮箱发送重置密码验证码."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # 不暴露邮箱是否已注册，统一提示
        return {"message": "如果该邮箱已绑定账号，验证码已发送"}
    try:
        send_verification(db, request.email, "reset_password")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    return {"message": "如果该邮箱已绑定账号，验证码已发送"}


@router.post("/reset-password", summary="重置密码")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """验证验证码并重置密码."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱未绑定账号")
    if not verify_code(db, request.email, request.code, "reset_password"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")
    user.password_hash = auth_service.hash_password(request.new_password)
    auth_service.invalidate_sessions(user)
    db.commit()
    return {"message": "密码已重置，请使用新密码登录"}


@router.post("/logout", summary="登出")
async def logout(user: User = Depends(get_current_user), req: Request = None, db: Session = Depends(get_db)):
    """登出（JWT 无状态，前端删除 token 即可）."""
    auth_service.log_auth(db, user.username, "logout", req.client.host if req and req.client else None)
    return {"message": "已登出"}


@router.get("/me", summary="当前用户信息")
async def me(user: User = Depends(get_current_user)):
    """获取当前登录用户信息."""
    return {"id": user.id, "username": user.username, "role": user.role}


@router.get("/logs", summary="认证日志（仅管理员）")
async def auth_logs(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    """查看认证日志，按时间倒序."""
    query = db.query(AuthLog).order_by(AuthLog.created_at.desc())
    total = query.count()
    records = query.offset(skip).limit(limit).all()

    items = [
        {
            "id": r.id,
            "username": r.username,
            "action": r.action,
            "ip_address": r.ip_address,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in records
    ]
    return {"total": total, "items": items}
