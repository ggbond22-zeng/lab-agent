from sqlalchemy.orm import Session
from model.user import User
from model.lab import Lab
from model.equipment import Equipment
from model.reservation import Reservation
from Schemas.reservation import ReservationCreateRequest, ReservationResponse
from datetime import datetime
from common.exceptions import BusinessException
from common.response import PageListResponse
from database import SessionLocal
import asyncio


def create_reservation(db: Session, current_user: User, data: ReservationCreateRequest):
    """ 创建预约信息 """

    # 先判断预约的时间是否符合
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M')

    if data.date < current_date:
        raise BusinessException(message='预约日期不能小于当前日期')

    if data.end_time < data.start_time:
        raise BusinessException(message='预约结束时间不能小于开始时间')

    if data.date == current_date and data.start_time < current_time:
        raise BusinessException(message='预约开始时间不能小于当前时间')

    # 判断实验室角度
    lab = db.query(Lab).filter(Lab.id == data.lab_id).first()

    if not lab:
        raise BusinessException(message='当前实验室不存在')

    if lab.status != 1:
        raise BusinessException(message='当前实验室未开放')

    if lab.open_time and data.start_time < lab.open_time:
        raise BusinessException(message='预约的开始时间不能小于实验室的开放时间')

    if lab.close_time and data.end_time > lab.close_time:
        raise BusinessException(message="预约的结束时间不能大于实验室的关闭时间")

    # 从实验室设备角度判断，如果没有equipment_id 代表预约的是实验室
    if data.equipment_id:
        equipment = db.query(Equipment).filter(Equipment.id == data.equipment_id).first()
        if not equipment:
            raise BusinessException(message='未找到当前实验室设备')

        if equipment.status != 1:
            raise BusinessException(message='当前设备正在维修')

    # 查看是否能够预约
    query = db.query(Reservation).filter(
        Reservation.lab_id == data.lab_id,   # 相同的实验室
        Reservation.date == data.date,    # 相同的日期
        Reservation.status.in_([0, 1]),    # 在 未审核和通过的状态
        Reservation.start_time > data.end_time,   # 如果预约的结束时间大于别人的开始时间，说明此时设备别人还在使用中
        Reservation.end_time < data.start_time  # 如果预约的开始时间小于于别人的结束时间，说明此时设备别人还在使用中
    )

    # 再判断是否预约实验室设备
    if data.equipment_id:
        query = query.filter(Reservation.equipment_id == data.equipment_id)
    else:
        query = query.filter(Reservation.equipment_id.is_(None))

    res = query.first()
    if res:
        raise BusinessException(message='该时段已被预约')

    # 将数据构造好
    reservation_model = Reservation(
        user_id = current_user.id,
        lab_id = data.lab_id,
        equipment_id = data.equipment_id,
        date = data.date,
        start_time = data.start_time,
        end_time = data.end_time,
        remark = data.remark,
        status = 0
    )

    db.add(reservation_model)
    db.commit()


def get_reservation_page_list(db: Session, current_user: User, page: int, page_size: int, status: int | None = None):
    """ 获取预约信息及其分页信息 """

    # 先查询一整个数据表
    query = db.query(Reservation)
    # 判断身份时管理员还是用户，如果是管理员可以看见全部的预约数据，用户自能看到自己的预约请求信息
    if current_user.role != 'admin':
        query = query.filter(Reservation.user_id == current_user.id)

    # 如果用户在前端根据预约状态进行查询
    if status is not None:
        query = query.filter(Reservation.status == status)

    # 得到查询到的总数
    total = query.count()

    # 进行分页查询
    items = query.order_by(Reservation.id.desc()).offset(( page - 1) * page_size).limit(page_size).all()

    # 将查询到的数据进行校验
    result = []
    for item in items:
        res = ReservationResponse.model_validate(item)

        # 因为校验模型中有些字段可以为None，再进行手动赋值更保险
        # 并且Reservation 是可以对之前的所有表进行关系查询
        res.user_name = item.user.name if item.user else None
        res.lab_name = item.lab.name if item.lab else None
        res.equipment_name = item.equipment.name if item.equipment else None
        res.type = '设备' if item.equipment_id else '实验室'
        result.append(res)

    return PageListResponse(list=result, total=total)


def get_reservation_page_list_home(
    db: Session,
    current_user: User,
    page: int,
    page_size: int,
    date: str | None = None,
    status: int = 1,
):
    """获取预约信息及其分页信息，用于在主页展示"""

    # 先查询一整个数据表
    query = db.query(Reservation)

    # 如果用户在前端根据预约状态进行查询
    if status is not None:
        query = query.filter(Reservation.status == status)

    if date is not None:
        query = query.filter(Reservation.date == date)

    now = datetime.now().strftime("%Y-%m-%d")
    query = query.filter(Reservation.date >= now)

    # 得到查询到的总数
    total = query.count()

    # 进行分页查询
    items = (
        query.order_by(Reservation.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 将查询到的数据进行校验
    result = []
    for item in items:
        res = ReservationResponse.model_validate(item)

        # 因为校验模型中有些字段可以为None，再进行手动赋值更保险
        # 并且Reservation 是可以对之前的所有表进行关系查询
        res.user_name = item.user.name if item.user else None
        res.lab_name = item.lab.name if item.lab else None
        res.equipment_name = item.equipment.name if item.equipment else None
        res.type = "设备" if item.equipment_id else "实验室"
        result.append(res)

    return PageListResponse(list=result, total=total)


def cancel_reservation(db: Session, current_user: User, reservation_id: int):
    """ 用户对预约进行取消 """
    data = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not data:
        raise BusinessException(message='预约记录不存在')
    
    if data.user_id != current_user.id:
        raise BusinessException(message='当前预约信息无权访问')

    if data.status != 0:
        raise BusinessException(message='当前状态不可取消')

    data.status = 3
    db.commit()


def audit_reservation(db: Session, reservation_id: int, status: int):
    """ 管理员对用户预约状态进行审批 """

    # 这是前端管理员审核后的状态
    if status not in [1, 2]:
        raise BusinessException(message='审核状态错误')

    data = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not data:
        raise BusinessException(message="预约记录不存在")
    if data.status != 0:
        raise BusinessException(message='当前状态不支持审批')

    data.status = status
    db.commit()


def expire_panding_reservation():
    """ 处理预约时间过期未审核的预约信息 """
    # 因为是自动执行函数，数据库无法传入获取，需要手动创建
    db = SessionLocal()

    try:
        # 获取当前时间
        now_date = datetime.now().strftime('%Y-%m-%d')
        now_time = datetime.now().strftime('%H:%M')

        # 查询数据库中的所有订单
        items = db.query(Reservation).filter(Reservation.status == 0).all()

        # 批量提交判断
        change = False
        for item in items:
            if item.date < now_date or (item.date == now_date and item.end_time < now_time):
                item.status = 3
                change = True
        # 将需要修改的信息进行批量提交
        if change:
            db.commit()

    # 修改或检查完成后自动关闭数据库连接
    finally:
        db.close()

async def run_expire_scan():
    """ 自动扫描所有的预约信息 """
    # 只要触发了函数就自动对全部的预约信息进行扫描
    while True:
        expire_panding_reservation()
        await asyncio.sleep(60)   # 一分钟执行一次
