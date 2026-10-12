from database import Base
from model.lab import Lab
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Equipment(Base):
    __tablename__ = 'equipments'
    __table_args__ = {'comment': '实验室设备信息表'}

    lab_id: Mapped[int] = mapped_column(ForeignKey('labs.id'), comment='所属实验室')
    name: Mapped[str] = mapped_column(String(50), comment='设备名称')
    description: Mapped[str] = mapped_column(String(500), comment='设备描述', nullable=True)
    img: Mapped[str] = mapped_column(String(500), comment="设备图片", nullable=True)
    spec: Mapped[str] = mapped_column(String(100), comment="型号规格", nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, comment='设备数量', default=1)
    status: Mapped[int] = mapped_column(Integer, comment="状态：0-维修，1-正常", default=1)

    # 关系查询，在查询该表时也同时将关系表进行查询
    lab: Mapped[Lab] = relationship()
