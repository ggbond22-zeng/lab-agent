from database import Base
from model.user import User
from model.lab import Lab
from model.equipment import Equipment
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Reservation(Base):
    __tablename__ = 'reservations'
    __table_args__ = {'comment': '预约信息表'}

    # 数据表字段
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), comment='用户ID')
    lab_id: Mapped[int] = mapped_column(ForeignKey('labs.id'), comment='实验室ID')
    equipment_id: Mapped[int] = mapped_column(ForeignKey('equipments.id'), comment='实验室设备ID', nullable=True)
    date: Mapped[str] = mapped_column(String(50), comment='预约日期')
    start_time: Mapped[str] = mapped_column(String(50), comment='预约开始时间')
    end_time: Mapped[str] = mapped_column(String(50), comment="预约结束时间")
    remark: Mapped[str] = mapped_column(String(500), comment='预约备注', nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=0, comment='0待审批 1已通过 2已拒绝 3取消')

    # 进行关系查询
    user: Mapped[User] = relationship()
    lab: Mapped[Lab] = relationship()
    equipment: Mapped[Equipment] = relationship()
