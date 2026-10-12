from database import Base
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

class Lab(Base):
    __tablename__ = 'labs'
    __table_args__ = {'comment': '实验室信息表'}

    name: Mapped[str] = mapped_column(String(50), comment='实验室名称')
    description: Mapped[str] = mapped_column(
        String(500), comment="实验室描述简介", nullable=True
    )
    capacity: Mapped[int] = mapped_column(Integer, default=1, comment='实验室人数容量')
    location: Mapped[str] = mapped_column(String(500), comment="实验室位置", nullable=True)
    open_time: Mapped[str] = mapped_column(
        String(50), comment="实验室开放时间", nullable=True
    )
    close_time: Mapped[str] = mapped_column(
        String(50), comment="实验室关闭时间", nullable=True
    )
    img: Mapped[str] = mapped_column(String(500), comment="实验室封面图", nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=1, comment='实验室开放状态 1:开放，0:关闭')
