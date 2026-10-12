from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from config import settings
from datetime import datetime

# SQLite 时允许多线程共用连接：FastAPI 的同步接口运行在线程池中，
# 默认 check_same_thread=True 会因"跨线程使用连接"报错（如 sqlite3.ProgrammingError）
engine_kwargs = {'pool_pre_ping': True, 'echo': True}
if settings.DATABASE_URL.startswith('sqlite'):
    engine_kwargs['connect_args'] = {'check_same_thread': False}

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

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
