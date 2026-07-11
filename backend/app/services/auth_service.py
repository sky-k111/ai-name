"""认证服务 — 注册、登录、JWT."""
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import User
from app.models.auth_log import AuthLog

# 北京时间 (UTC+8)
CST = timezone(timedelta(hours=8))

def beijing_now() -> datetime:
    """返回当前北京时间."""
    return datetime.now(CST)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """密码 → bcrypt 哈希."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希是否匹配."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, token_version: int = 0) -> str:
    """生成 JWT token."""
    expire = datetime.now(CST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),  # JWT spec 要求 sub 为字符串
        "ver": token_version,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def register_user(db: Session, username: str, password: str) -> User:
    """注册新用户。用户名已存在则抛异常."""
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise ValueError("用户名已被注册")

    user = User(
        username=username,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, username: str, password: str) -> str:
    """登录校验，成功返回 JWT token."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise ValueError("用户名或密码错误")
    if not verify_password(password, user.password_hash):
        raise ValueError("用户名或密码错误")
    return create_access_token(user.id, user.token_version)


def log_auth(db: Session, username: str, action: str, ip_address: str | None = None):
    """记录认证行为到数据库."""
    log = AuthLog(username=username, action=action, ip_address=ip_address)
    db.add(log)
    db.commit()


def init_admin(db: Session, username: str, password: str):
    """确保管理员账号存在；启动时不重置现有账号密码或角色."""
    if not username or not password:
        return
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return
    user = User(
        username=username,
        password_hash=hash_password(password),
        role="admin",
    )
    db.add(user)
    db.commit()


def invalidate_sessions(user: User) -> None:
    """使该用户现有 JWT 立即失效。"""
    user.token_version += 1
