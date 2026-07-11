"""应用配置."""
import os

from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件中的环境变量

# 数据库 — 默认 SQLite，设置 DATABASE_URL 环境变量切换 MySQL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:rootpassword@localhost:3306/naming_db")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
IS_PRODUCTION = ENVIRONMENT in {"production", "prod"}

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "" if IS_PRODUCTION else "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时

# 管理员 — 生产环境必须显式配置；开发环境保留便于本地启动的默认值
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "" if IS_PRODUCTION else "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "" if IS_PRODUCTION else "admin123456")
ENABLE_DEMO_RECHARGE = os.getenv("ENABLE_DEMO_RECHARGE", "false").strip().lower() == "true"


def validate_runtime_config() -> None:
    """生产环境拒绝已知默认凭据和空 JWT 密钥。"""
    if not IS_PRODUCTION:
        return
    if len(SECRET_KEY) < 32:
        raise RuntimeError("生产环境必须配置至少 32 字符的 SECRET_KEY")
    if not ADMIN_USERNAME or not ADMIN_PASSWORD or ADMIN_PASSWORD in {"admin123456", "password", "change-me"}:
        raise RuntimeError("生产环境必须显式配置非默认管理员凭据")

# SMTP 邮件
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")
