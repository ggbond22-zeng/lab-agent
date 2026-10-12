"""
一次性数据迁移脚本：本地 MySQL → TiDB Cloud

用法（在 backend 目录下执行）：
  python scripts/migrate_to_tidb.py "mysql+pymysql://<用户名>:<密码>@<主机>:4000/<库名>"

说明：
- 源库连接串自动读取 backend/.env 里的 DATABASE_URL（本地库）
- 目标库是命令行传入的 TiDB 连接串（不用带 ssl 参数，脚本会自动加）
- 4 张表全量复制，目标表先清空再写入，因此可以重复执行（幂等）
- 若密码里含 @ : / 等特殊字符，需先做 URL 编码（如 @ → %40）
"""
import sys
from pathlib import Path

# 把 app 目录加入 sys.path，才能像后端一样导入 config / model / database
APP_DIR = Path(__file__).resolve().parent.parent / 'app'
sys.path.insert(0, str(APP_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import certifi

from model.user import User
from model.lab import Lab
from model.equipment import Equipment
from model.reservation import Reservation
from database import Base

# 按依赖顺序排列：被外键引用的表先复制（labs → equipments，users/labs → reservations）
TABLES = [User, Lab, Equipment, Reservation]


def make_engine(url: str, is_tidb: bool):
    kwargs = dict(pool_pre_ping=True)
    if is_tidb:
        # TiDB Cloud 强制 TLS 连接，处理逻辑与 app/database.py 保持一致
        kwargs['connect_args'] = {'ssl_verify_cert': True, 'ssl_ca': certifi.where()}
    return create_engine(url, **kwargs)


def copy_table(src_db, dst_db, model) -> int:
    """目标表先清空，再从源表全量复制，返回复制的行数"""
    rows = src_db.query(model).all()
    dst_db.query(model).delete()
    for row in rows:
        # 按列名逐列取值，自动排除 SQLAlchemy 的内部状态属性 _sa_instance_state
        data = {c.name: getattr(row, c.name) for c in model.__table__.columns}
        dst_db.add(model(**data))
    dst_db.commit()
    return len(rows)


def main():
    if len(sys.argv) < 2:
        print('用法: python scripts/migrate_to_tidb.py "<TiDB连接串>"')
        sys.exit(1)

    tidb_url = sys.argv[1]
    # 导入 config 会读取 backend/.env，从而拿到本地库连接串
    from config import settings

    src_engine = make_engine(settings.DATABASE_URL, is_tidb=False)
    dst_engine = make_engine(tidb_url, is_tidb=True)

    # 在目标库建表（建表语句与应用启动时完全一致）
    Base.metadata.create_all(bind=dst_engine)

    src_db = sessionmaker(bind=src_engine)()
    dst_db = sessionmaker(bind=dst_engine)()

    try:
        total = 0
        for model in TABLES:
            count = copy_table(src_db, dst_db, model)
            total += count
            print(f'{model.__table__.name:<15} 复制 {count} 行')
        print(f'迁移完成，共 {total} 行')
    finally:
        src_db.close()
        dst_db.close()


if __name__ == '__main__':
    main()
