"""管理后台路由 — 仅管理员."""
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_admin
from app.models.naming_history import NamingHistory
from app.models.auth_log import AuthLog
from app.models.user import User
from app.services import auth_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


class NamingSummary(BaseModel):
    id: int
    username: str
    surname: str
    gender: str
    names_count: int
    is_deleted: bool
    created_at: str


class NamingListResponse(BaseModel):
    total: int
    items: list[NamingSummary]


class UserSummary(BaseModel):
    id: int
    username: str
    email: str | None
    role: str
    is_deleted: bool
    created_at: str
    naming_count: int


class UserListResponse(BaseModel):
    total: int
    items: list[UserSummary]


@router.get("/namings", response_model=NamingListResponse, summary="全部取名记录（仅管理员）")
async def all_namings(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    """管理员查看所有人的取名记录."""
    query = db.query(NamingHistory).order_by(NamingHistory.created_at.desc())
    total = query.count()
    records = query.offset(skip).limit(limit).all()

    # 获取所有相关用户的 username
    user_ids = list(set(r.user_id for r in records))
    users = {u.id: u.username for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    items = []
    for r in records:
        try:
            names = json.loads(r.result_json)
        except (json.JSONDecodeError, TypeError):
            names = []
        items.append(
            NamingSummary(
                id=r.id,
                username=users.get(r.user_id, f"用户#{r.user_id}"),
                surname=r.surname,
                gender=r.gender,
                names_count=len(names) if isinstance(names, list) else 0,
                is_deleted=r.is_deleted,
                created_at=r.created_at.isoformat() if r.created_at else "",
            )
        )
    return {"total": total, "items": items}


@router.get("/users", response_model=UserListResponse, summary="全部用户列表（仅管理员）")
async def all_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """管理员查看所有未注销用户及其取名次数."""
    users = db.query(User).filter(User.is_deleted == False).order_by(User.created_at.desc()).all()
    items = []
    for u in users:
        naming_count = db.query(NamingHistory).filter(NamingHistory.user_id == u.id).count()
        items.append(
            UserSummary(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role,
                is_deleted=u.is_deleted,
                created_at=u.created_at.isoformat() if u.created_at else "",
                naming_count=naming_count,
            )
        )
    return {"total": len(items), "items": items}


class ResetPasswordRequest(BaseModel):
    user_id: int
    new_password: str = Field(..., min_length=6, max_length=100)


@router.put("/reset-password", summary="管理员重置用户密码")
async def admin_reset_password(
    request: ResetPasswordRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """管理员强制重置某用户的密码."""
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.role == "admin" and user.id != admin.id:
        raise HTTPException(status_code=403, detail="不能重置其他管理员的密码")
    user.password_hash = auth_service.hash_password(request.new_password)
    auth_service.invalidate_sessions(user)
    db.commit()
    return {"message": f"用户 {user.username} 的密码已重置"}


@router.get("/active-users", response_model=UserListResponse, summary="今日活跃用户（仅管理员）")
async def active_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """管理员查看今日有操作的用户."""
    from datetime import datetime, timezone, timedelta
    CST = timezone(timedelta(hours=8))
    today_start = datetime.now(CST).replace(hour=0, minute=0, second=0, microsecond=0)

    today_logs = (
        db.query(AuthLog.username)
        .filter(AuthLog.created_at >= today_start)
        .distinct()
        .all()
    )
    active_usernames = set(row[0] for row in today_logs)

    users = db.query(User).filter(User.username.in_(active_usernames)).all() if active_usernames else []
    items = []
    for u in users:
        naming_count = db.query(NamingHistory).filter(NamingHistory.user_id == u.id).count()
        items.append(
            UserSummary(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role,
                is_deleted=u.is_deleted,
                created_at=u.created_at.isoformat() if u.created_at else "",
                naming_count=naming_count,
            )
        )
    return {"total": len(items), "items": items}
