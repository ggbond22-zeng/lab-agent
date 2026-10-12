from pydantic import BaseModel, ConfigDict


class LabResponse(BaseModel):
    """实验室响应参数模型，用于返回给前端的响应数据"""

    id: int  # 用户ID 前端的编辑和删除操作都需要用到
    name: str
    description: str | None = None
    capacity: int
    location: str | None = None  # 可选字段，允许为 None，如果数据库中该字段为空，则返回 None
    open_time: str | None = None
    close_time: str | None = None
    img: str | None = None
    status: int

    model_config = ConfigDict(
        from_attributes=True
    )  # 允许从 ORM 模型中读取数据，即数据库中的User 实例可以直接转换为 UserResponse 实例，而不需要手动赋值。


class CreateLabRequest(BaseModel):
    """创建实验室请求参数校验模型"""

    name: str
    description: str | None = None
    capacity: int = 1
    location: str | None = None
    open_time: str | None = None
    close_time: str | None = None
    img: str | None = None
    status: int | None = 1  # 可选字段，允许为 None


class UpdateLabRequest(BaseModel):
    """更新实验室信息请求参数校验模型"""

    name: str | None = None
    description: str | None = None
    capacity: int | None = None
    location: str | None = None
    open_time: str | None = None
    close_time: str | None = None
    img: str | None = None
    status: int | None = 1  # 可选字段，允许为 None
