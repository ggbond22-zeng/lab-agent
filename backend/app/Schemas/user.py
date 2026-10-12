from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    """登录响应参数模型，用于返回给前端的登录响应数据"""
    id: int   # 用户ID 前端的编辑和删除操作都需要用到
    username: str
    name: str
    role: str
    email: str | None = None
    phone: str | None = None   # 可选字段，允许为 None，如果数据库中该字段为空，则返回 None
    avatar: str | None = None
    status: int

    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 模型中读取数据，即数据库中的
    # User 实例可以直接转换为 UserResponse 实例，而不需要手动赋值。

class CreateUserRequest(BaseModel):
    """ 创建用户请求参数校验模型 """
    username: str
    password: str = '123'
    name: str | None = None
    role: str = 'student'
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    status: int | None = 1  # 可选字段，允许为 None


class UpdateUserInfoRequest(BaseModel):
    """ 更新用户信息请求参数校验模型 """
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    status: int | None = None  # 可选字段，允许为 None，如果数据库中该字段为空，则返回 None
    role: str | None = None



class UpdatePasswordRequest(BaseModel):
    """ 更新用户密码参数模型 """
    old_password: str
    new_password: str
