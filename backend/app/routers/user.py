"""用户中心路由."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.naming_history import NamingHistory
from app.models.favorite import Favorite
from app.services import auth_service
from app.services.email_service import send_verification, verify_code

router = APIRouter(prefix="/api/user", tags=["user"])


# ── Models ──────────────────────────────────────────────────


class UpdateProfileRequest(BaseModel):
    nickname: str | None = Field(None, max_length=50)
    username: str | None = Field(None, min_length=2, max_length=50)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class BindEmailRequest(BaseModel):
    email: str = Field(..., max_length=100)


class VerifyEmailRequest(BaseModel):
    email: str
    code: str = Field(..., min_length=6, max_length=6)


class UploadAvatarRequest(BaseModel):
    avatar: str = Field(..., max_length=500000, description="base64 编码的图片")


# ── Routes ──────────────────────────────────────────────────


@router.put("/profile", summary="修改个人资料")
async def update_profile(
    request: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改昵称或用户名."""
    if request.nickname is not None:
        user.nickname = request.nickname.strip() or None
    if request.username is not None:
        existing = db.query(User).filter(User.username == request.username, User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=409, detail="用户名已被使用")
        user.username = request.username.strip()
    db.commit()
    return {"message": "已更新", "nickname": user.nickname, "username": user.username}


@router.put("/password", summary="修改密码")
async def change_password(
    request: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码（需旧密码验证）."""
    if not auth_service.verify_password(request.old_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误")
    user.password_hash = auth_service.hash_password(request.new_password)
    auth_service.invalidate_sessions(user)
    db.commit()
    return {"message": "密码已修改"}


@router.post("/email/bind", summary="发送绑定邮箱验证码")
async def bind_email_send(
    request: BindEmailRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """发送验证码到指定邮箱."""
    # 检查邮箱是否已被其他用户绑定
    existing = db.query(User).filter(User.email == request.email, User.id != user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该邮箱已被其他用户绑定")
    try:
        send_verification(db, request.email, "bind")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    return {"message": "验证码已发送"}


@router.post("/email/verify", summary="确认绑定邮箱")
async def bind_email_verify(
    request: VerifyEmailRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """验证验证码并绑定邮箱."""
    if not verify_code(db, request.email, request.code, "bind"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")
    user.email = request.email
    db.commit()
    return {"message": "邮箱绑定成功", "email": user.email}


@router.post("/avatar", summary="上传头像")
async def upload_avatar(
    request: UploadAvatarRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传头像（base64）."""
    user.avatar = request.avatar
    db.commit()
    return {"message": "头像已更新"}


@router.delete("/account", summary="注销账号")
async def delete_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """注销账号。删除所有个人数据，认证日志保留."""
    auth_service.log_auth(db, user.username, "delete_account")
    # 删除所有取名历史 + 用户（认证日志保留）
    db.query(NamingHistory).filter(NamingHistory.user_id == user.id).delete()
    db.delete(user)
    db.commit()
    return {"message": "账号已注销"}


@router.get("/stats", summary="个人取名统计")
async def get_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取个人取名统计数据."""
    total = db.query(NamingHistory).filter(NamingHistory.user_id == user.id, NamingHistory.is_deleted == False).count()
    by_type = {}
    for t in ["naming", "analyze", "compare", "premium"]:
        cnt = db.query(NamingHistory).filter(
            NamingHistory.user_id == user.id,
            NamingHistory.is_deleted == False,
            NamingHistory.record_type == t
        ).count()
        if cnt > 0: by_type[t] = cnt
    favorites = db.query(Favorite).filter(Favorite.user_id == user.id).count()
    return {"total_namings": total, "by_type": by_type, "favorites": favorites}


@router.get("/export", summary="导出个人数据")
async def export_data(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """导出个人全部数据为 JSON."""
    import json as j
    history = (
        db.query(NamingHistory)
        .filter(NamingHistory.user_id == user.id, NamingHistory.is_deleted == False)
        .order_by(NamingHistory.created_at.desc()).all()
    )
    favs = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    data = {
        "user": {"username": user.username, "email": user.email, "role": user.role},
        "history": [{"id": h.id, "surname": h.surname, "gender": h.gender, "type": h.record_type, "result": j.loads(h.result_json) if h.result_json else [], "created_at": h.created_at.isoformat() if h.created_at else ""} for h in history],
        "favorites": [{"full_name": f.full_name, "data": j.loads(f.name_data) if f.name_data else {}} for f in favs],
    }
    return data


@router.get("/profile", summary="获取个人资料")
async def get_profile(
    user: User = Depends(get_current_user),
):
    """获取当前用户的完整资料."""
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "avatar": user.avatar,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else "",
    }
