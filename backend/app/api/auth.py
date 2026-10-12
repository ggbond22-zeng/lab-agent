from fastapi import APIRouter, Depends
from database import get_db
from Schemas.auth import LoginRequest,RegisterRequest
from sqlalchemy.orm import Session
from common.response import Response
from services import auth as auth_service

router = APIRouter(prefix='/auth', tags=['权限验证'])

# Depends 是依赖导入的功能 有了Depends 就可以使用 get_db 中的 yield db
# 登录功能必须要使用 post 请求，如果使用 get 请求，用户在登录后参数会暴露在路径中，有风险
@router.post('/login')
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """处理用户登录请求，验证用户名和密码是否正确"""
    result = auth_service.login(db, data)

    # 登录成功后前端收到的响应结果
    return Response.success(
        message="登录成功",
        # 因为此时 user 的数据类型是从 orm 中读取的数据类型 要先将其转换为 pydantic 类型才能传入 LoginResponse 中进行校验
        data=result,
    )


@router.post("/register")
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """ 注册功能 """
    auth_service.register(db, data)

    return Response.success(message="注册成功",)
