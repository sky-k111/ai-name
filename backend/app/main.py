"""AI 智能取名系统 — FastAPI 入口."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY, IS_PRODUCTION, validate_runtime_config
from app.database import init_db, SessionLocal
from app.routers import naming, auth, admin, user, payment, favorites
from app.services.auth_service import init_admin
from app.middleware.security import rate_limit_middleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时初始化数据库表 + 创建管理员."""
    validate_runtime_config()
    init_db()
    db = SessionLocal()
    try:
        init_admin(db, ADMIN_USERNAME, ADMIN_PASSWORD)
    finally:
        db.close()
    yield


app = FastAPI(
    title="AI 智能取名系统",
    description="基于 DeepSeek 大语言模型的智能取名服务",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — 允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(naming.router, prefix="/api/naming", tags=["naming"])
app.include_router(auth.router, tags=["auth"])
app.include_router(admin.router, tags=["admin"])
app.include_router(user.router, tags=["user"])
app.include_router(payment.router, tags=["payment"])
app.include_router(favorites.router, tags=["favorites"])

# 安全中间件：频率限制
app.middleware("http")(rate_limit_middleware)

# 启动时检查 JWT 密钥
if not IS_PRODUCTION and SECRET_KEY == "dev-secret-key-change-in-production":
    logging.warning("⚠️ JWT SECRET_KEY 使用默认值！生产环境请设置环境变量 SECRET_KEY")


@app.get("/api/health")
async def health_check():
    """健康检查."""
    return {"status": "ok", "service": "ai-naming"}
