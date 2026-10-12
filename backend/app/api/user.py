from fastapi import APIRouter, Depends
from Schemas.user import UserResponse, UpdateUserInfoRequest, UpdatePasswordRequest, CreateUserRequest
from model.user import User
from dependencies.auth import get_current_user, get_current_admin
from common.response import Response
from services import user_service
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/user", tags=["用户信息接口"])


# Depends 是依赖导入的功能 有了Depends 就可以使用 get_db 中的 yield db
# 登录功能必须要使用 post 请求，如果使用 get 请求，用户在登录后参数会暴露在路径中，有风险
@router.get("/info")
async def get_user_info(current_user: User = Depends(get_current_user)):
    """ 对当前用户进行鉴权验证 获取当前登录用户信息"""

    # 因为此时 user 的数据类型是从 orm 中读取的数据类型 要先将其转换为 pydantic 类型才能传入 LoginResponse 中进行校验
    return Response.success(data=user_service.get_user_info(current_user))


@router.put('/update')
async def update_user_info(data: UpdateUserInfoRequest, 
                           current_user: User = Depends(get_current_user), 
                           db: Session = Depends(get_db)
                           ):
    """ 修改用户信息 """
    res = user_service.update_user_info(db, current_user, data)

    return Response.success(data=res)


@router.put('/password')
async def update_password(
    data: UpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """ 修改密码 """
    user_service.update_password(db, current_user, data)

    return Response.success()

@router.get('/list')
async def get_user_list(page: int = 1, 
                        page_size: int = 10, 
                        keyword: str = '', 
                        db: Session = Depends(get_db), 
                        current_user: User = Depends(get_current_admin)
                ):
    """ 获取用户列表和分页信息 """
    res = user_service.get_user_list(db, page, page_size, keyword)
    return Response.success(data=res)


@router.post('')
async def create_user(
    data: CreateUserRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """ 创建用户 """
    res = user_service.create_user(db, data)
    return Response.success(data=res)


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    data: UpdateUserInfoRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """更新用户"""
    res = user_service.update_user(db, user_id, data)
    return Response.success(data=res)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """删除用户"""
    user_service.delete_user(db, user_id, current_user)
    return Response.success()
