from fastapi import APIRouter, Depends
from Schemas.equipment import CreateEquipmentRequest, UpdateEquipmentRequest, EquipmentResponse
from model.user import User
from dependencies.auth import get_current_admin, get_current_user
from common.response import Response
from services import equipment_service
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/equipment", tags=["实验室设备信息接口"])


@router.get("/list")
async def get_equipment_list(
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = "",
    db: Session = Depends(get_db),
    lab_id: int | None = None,
    current_user: User = Depends(get_current_user),
):
    """获取实验室设备列表和分页信息"""

    res = equipment_service.get_Equipment_list(db, page, page_size, keyword, lab_id)
    return Response.success(data=res)


@router.post("")
async def create_equipment(
    data: CreateEquipmentRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """创建实验室设备"""

    res = equipment_service.create_Equipment(db, data)
    return Response.success(data=res)


@router.put("/{equipment_id}")
async def update_equipment(
    equipment_id: int,
    data: UpdateEquipmentRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """更新实验室设备"""

    res = equipment_service.update_Equipment(db, equipment_id, data)
    return Response.success(data=res)


@router.delete("/{equipment_id}")
async def delete_equipment(
    equipment_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """删除实验室设备"""

    equipment_service.delete_Equipment(db, equipment_id)
    return Response.success()
