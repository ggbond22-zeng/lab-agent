from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from config import settings
from datetime import datetime
import certifi

# TiDB Cloud（云端数据库）强制要求 TLS 加密连接，需要指定 CA 证书来校验服务端身份
# 连接串里包含 tidbcloud.com 时才启用，本地 MySQL（127.0.0.1）不受影响
connect_args = {}
if 'tidbcloud.com' in settings.DATABASE_URL:
    connect_args.update(ssl_verify_cert=True, ssl_ca=certifi.where())

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=True, connect_args=connect_args)

# 连接数据库会话工厂
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# 创建全局连接数据库
def get_db():
    db = SessionLocal()
    try:
        yield db    # 生成器函数，返回数据库会话对象，就是将数据库会话对象传递给调用者
    finally:
        db.close()   # 数据库操作完成后关闭数据库连接

# 创建模型基类
# 因为在创建数据表时，基类总是会放在后面，如果想让id放在第一位，可以使用sort_order进行排序，-1表示固定在表单的第一行
class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, sort_order=-1, comment="主键ID")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, sort_order=1, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, sort_order=2, comment="更新时间")
