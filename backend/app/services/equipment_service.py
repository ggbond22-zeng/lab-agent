from model.equipment import Equipment
from operator import or_
from sqlalchemy.orm import Session
from common.response import PageListResponse
from common.exceptions import BusinessException
from Schemas.equipment import EquipmentResponse, CreateEquipmentRequest, UpdateEquipmentRequest


def get_Equipment_list(db: Session, page: int, page_size: int, keyword: str, lab_id: int):
    """获取实验室列表和分页信息"""
    query = db.query(Equipment)

    # 先对用户输入的关键字进行模糊查询
    if keyword:
        query = query.filter(Equipment.name.ilike(f"%{keyword}%"))

    # 再根据实验室进行查询
    if lab_id:
        query = query.filter(Equipment.lab_id == lab_id)

    # 获取总页数
    total = query.count()
    # 分页查询  offset((page - 1) * page_size) 是查询的起始位置 limit(page_size) 是查询的条数
    items = (
        query.order_by(Equipment.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 因为在EquipmentResponse中还有lab_name字段，但是Equipment模型中没有该字段，要进行手动添加
    result = []
    for item in items:
        data = EquipmentResponse.model_validate(item)
        # 因为Equipment模型中有关联查询Lab表，如果查找到了Lab表中的内容，就将lab_name拿出来添加到Response中
        data.lab_name = item.lab.name if item.lab else None
        result.append(data)

    # 因为items 是从 orm 中读取的数据类型，要先将其转换为 pydantic 类型 在 EquipmentResponse 中进行校验
    return PageListResponse(list=result, total=total)


def create_Equipment(db: Session, data: CreateEquipmentRequest):
    """创建实验室"""
    # 先查询是否存在相同名称的实验室设备
    exist = db.query(Equipment).filter(Equipment.name == data.name).first()
    if exist:
        raise BusinessException(message="该实验室设备名称已存在")

    # 将数据添加到 orm 模型中
    equipment = Equipment(**data.model_dump())

    # 添加到数据库中
    db.add(equipment)
    db.commit()
    db.refresh(equipment)

    # 再将lab_name字段 添加到EquipmentResponse中
    res = EquipmentResponse.model_validate(equipment)
    res.lab_name = equipment.lab.name if equipment.lab else None

    return res


def update_Equipment(db: Session, equipment_id: int, data: UpdateEquipmentRequest):
    """更新实验室"""
    # 先查询是否存在需要更新的实验室设备
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise BusinessException(message="未找到该实验室设备")

    # 将数据解析为字典
    payload = data.model_dump(exclude_none=True)
    # 此时的payload里面已经是转化为字典的data数据
    lab_id = payload.get('lab_id', equipment.lab_id)
    name = payload.get('name', equipment.name)

    # 再判断是否出现与想要更新的名称重名的情况
    exist = db.query(Equipment).filter(
        Equipment.id != equipment_id,    # 不同的设备id
        Equipment.lab_id == lab_id,   # 所属相同的实验室
        Equipment.name == name    # 设备名称相同
    ).first()   # 一定要记得加上first 否则得到只是查询的 mysql语句 下面的判断就会一直触发
    
    # 当3个条件全部满足时才会查询到数据
    if exist:
        raise BusinessException(message="不能有相同的实验室设备")

    # 将前端输入的数据替换到后端的 orm 模型中
    for filter, value in payload.items():
        setattr(equipment, filter, value)

    # 提交到数据库中
    db.commit()
    db.refresh(equipment)

    # 再将lab_name字段 添加到EquipmentResponse中
    res = EquipmentResponse.model_validate(equipment)
    res.lab_name = equipment.lab.name if equipment.lab else None

    return res


def delete_Equipment(db: Session, equipment_id: int):
    """删除实验室"""

    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise BusinessException(message="当前实验室不存在")

    db.delete(equipment)
    db.commit()
