from model.lab import Lab
from operator import or_
from sqlalchemy.orm import Session
from common.response import PageListResponse
from common.exceptions import BusinessException
from Schemas.lab import (
    LabResponse,
    CreateLabRequest,
    UpdateLabRequest
)


def get_Lab_list(db: Session, page: int, page_size: int, keyword: str, status: int):
    """获取实验室列表和分页信息"""
    query = db.query(Lab)

    # 先对用户输入的关键字进行模糊查询
    if keyword:
        query = query.filter(
            or_(Lab.name.ilike(f"%{keyword}%"), Lab.location.ilike(f'%{keyword}%'))
        )

    # 再根据实验室状态进行查询，展示给用户时展示status = 1的
    if status:
        query = query.filter(Lab.status == status)

    # 获取总页数
    total = query.count()
    # 分页查询  offset((page - 1) * page_size) 是查询的起始位置 limit(page_size) 是查询的条数
    items = (
        query.order_by(Lab.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 因为items 是从 orm 中读取的数据类型，要先将其转换为 pydantic 类型 在 LabResponse 中进行校验
    return PageListResponse(
        list=[LabResponse.model_validate(item) for item in items], total=total
    )


def get_Lab(db: Session, lab_id: int):
    """获取对应实验室信息"""
    lab = db.query(Lab).filter(Lab.id == lab_id).first()

    if not lab:
        raise BusinessException(message="该实验室不存在")

    return LabResponse.model_validate(lab)


def create_Lab(db: Session, data: CreateLabRequest):
    """创建实验室"""
    # 先查询是否存在相同名称的实验室
    exist = db.query(Lab).filter(Lab.name == data.name).first()
    if exist:
        raise BusinessException(message="该实验室名称已存在")
    
    # 将数据添加到 orm 模型中
    lab = Lab(**data.model_dump())

    # 添加到数据库中
    db.add(lab)
    db.commit()
    db.refresh(lab)

    return LabResponse.model_validate(lab)


def update_Lab(db: Session, lab_id: int, data: UpdateLabRequest):
    """更新实验室"""
    # 先查询是否存在需要更新的实验室
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise BusinessException(message="未找到该实验室")

    # 将数据解析为字典
    payload = data.model_dump(exclude_none=True)

    # 将前端输入的数据替换到后端的 orm 模型中
    for filter, value in payload.items():
        setattr(lab, filter, value)

    # 提交到数据库中
    db.commit()
    db.refresh(lab)

    return LabResponse.model_validate(lab)


def delete_Lab(db: Session, lab_id: int):
    """删除实验室"""

    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise BusinessException(message="当前实验室不存在")

    db.delete(lab)
    db.commit()
