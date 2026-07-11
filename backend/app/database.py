"""数据库连接 — SQLAlchemy."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import DATABASE_URL

# SQLite 需要 check_same_thread=False
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)


from datetime import datetime, timezone, timedelta

def beijing_now():
    """返回北京时间."""
    return datetime.now(timezone(timedelta(hours=8))).replace(tzinfo=None)


# SQLite pragma: use local time
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if DATABASE_URL.startswith("sqlite"):
        dbapi_connection.execute("PRAGMA journal_mode=WAL")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖 — 每个请求一个 session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建所有表 + 迁移已有表（不删数据）."""
    Base.metadata.create_all(bind=engine)
    _migrate()


def _migrate():
    """增量迁移——给已有表添加新字段，不删数据."""
    import sqlite3
    from sqlalchemy import inspect, text

    conn = engine.connect()
    inspector = inspect(engine)

    # users 表新增字段
    if "users" in inspector.get_table_names():
        cols = [c["name"] for c in inspector.get_columns("users")]
        migrations = [
            ("email", "VARCHAR(100)"),
            ("avatar", "TEXT"),
            ("nickname", "VARCHAR(50)"),
            ("is_deleted", "BOOLEAN DEFAULT 0"),
            ("balance", "FLOAT DEFAULT 0"),
            ("vip_level", "VARCHAR(10) DEFAULT 'free'"),
            ("vip_expire_at", "DATETIME"),
            ("daily_free_used", "INTEGER DEFAULT 0"),
            ("daily_exp_used", "BOOLEAN DEFAULT 0"),
            ("token_version", "INTEGER DEFAULT 0"),
        ]

        # naming_history 新增字段
        if "naming_history" in inspector.get_table_names():
            nh_cols = [c["name"] for c in inspector.get_columns("naming_history")]
            nh_migrations = [
                ("record_type", "VARCHAR(20) DEFAULT 'naming'"),
            ]
            for col_name, col_type in nh_migrations:
                if col_name not in nh_cols:
                    conn.execute(text(f"ALTER TABLE naming_history ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
        for col_name, col_type in migrations:
            if col_name not in cols:
                if engine.dialect.name == "sqlite":
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                else:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                conn.commit()
    conn.close()
