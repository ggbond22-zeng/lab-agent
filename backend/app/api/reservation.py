from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.auth import get_current_user, get_current_admin
from common.response import Response
from database import get_db
from services import reservation_service
from model.user import User
from Schemas.reservation import ReservationCreateRequest, AuditReservationRequest

router = APIRouter(prefix='/reservation', tags=['预约接口'])

@router.post('')
async def create_reservation(
    data: ReservationCreateRequest,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user), 
):
    """ 创建预约信息 """
    reservation_service.create_reservation(db, current_user, data)
    return Response.success()

@router.get('/list')
async def get_reservation_page_list(
    status: int | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
):
    """ 获取预约信息及其分页信息 """
    res = reservation_service.get_reservation_page_list(db, current_user, page, page_size, status)
    return Response.success(data=res)


@router.get("/list/home")
async def get_reservation_page_list_home(
    date: str | None = None,
    status: int | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取预约信息及其分页信息"""
    # 前端日期清空后会传 date=''（空字符串），空串不等于 None，会把查询条件变成 date == '' 导致查不到数据
    # 因此这里统一把空字符串归一化为 None，视为未传该参数
    date = date or None
    res = reservation_service.get_reservation_page_list_home(
        db, current_user, page, page_size, date, status
    )
    return Response.success(data=res)


@router.put('/{reservation_id}/cancel')
async def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """ 用户对预约进行取消 """
    reservation_service.cancel_reservation(db, current_user, reservation_id)
    return Response.success()

@router.put('/{reservation_id}/audit')
async def audit_reservation(
    reservation_id: int,
    data: AuditReservationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """ 管理员对用户预约状态进行审批 """
    reservation_service.audit_reservation(db, reservation_id, data.status)
    return Response.success()
