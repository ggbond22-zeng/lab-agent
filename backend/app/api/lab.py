from fastapi import APIRouter, Depends
from Schemas.lab import (
    CreateLabRequest,
    UpdateLabRequest,
    LabResponse
)
from model.user import User
from dependencies.auth import get_current_admin, get_current_user
from common.response import Response
from services import lab_service
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/lab", tags=["实验室信息接口"])


@router.get("/list")
async def get_lab_list(
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    status: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取实验室列表和分页信息"""
    res = lab_service.get_Lab_list(db, page, page_size, keyword, status)
    return Response.success(data=res)


@router.get("/{lab_id}")
async def get_lab(
    db: Session = Depends(get_db),
    lab_id: int = None,
    current_user: User = Depends(get_current_user),
):
    """获取对应实验室信息"""
    res = lab_service.get_Lab(db, lab_id)
    return Response.success(data=res)


@router.post("")
async def create_lab(
    data: CreateLabRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """创建实验室"""
    res = lab_service.create_Lab(db, data)
    return Response.success(data=res)


@router.put("/{lab_id}")
async def update_lab(
    lab_id: int,
    data: UpdateLabRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """更新实验室"""
    res = lab_service.update_Lab(db, lab_id, data)
    return Response.success(data=res)


@router.delete("/{lab_id}")
async def delete_lab(
    lab_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """删除实验室"""
    lab_service.delete_Lab(db, lab_id)
    return Response.success()
