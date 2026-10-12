from pydantic import BaseModel, Field
from Schemas.user import UserResponse

class LoginRequest(BaseModel):
    """登录请求参数模型,用于校验前端传入的登录请求参数"""
    username: str = Field(description='账号')
    password: str = Field(description='密码')

class LoginResponse(BaseModel):
    """ 对登录成功后的传入前端的数据进行校验 """
    token: str
    user: UserResponse


class RegisterRequest(BaseModel):
    """注册请求请求参数模型,用于校验前端传入的登录请求参数"""

    username: str 
    password: str 
    name: str | None = None
