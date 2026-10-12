from pydantic import BaseModel, ConfigDict


class EquipmentResponse(BaseModel):
    """实验室设备响应参数模型，用于返回给前端的响应数据"""

    id: int  # 用户ID 前端的编辑和删除操作都需要用到
    lab_id: int
    lab_name: str | None = None
    name: str 
    description: str | None = None
    img: str | None = None  # 可选字段，允许为 None，如果数据库中该字段为空，则返回 None
    spec: str | None = None
    quantity: int
    status: int

    model_config = ConfigDict(
        from_attributes=True
    )  # 允许从 ORM 模型中读取数据，即数据库中的User 实例可以直接转换为 UserResponse 实例，而不需要手动赋值。


class CreateEquipmentRequest(BaseModel):
    """创建实验室设备请求参数校验模型"""

    lab_id: int
    name: str 
    description: str | None = None
    img: str | None = None  # 可选字段，允许为 None，如果数据库中该字段为空，则返回 None
    spec: str | None = None
    quantity: int | None = 1
    status: int | None = 1  # 可选字段，允许为 None


class UpdateEquipmentRequest(BaseModel):
    """更新实验室设备信息请求参数校验模型"""

    lab_id: int | None = None
    name: str | None = None
    description: str | None = None
    img: str | None = None  # 可选字段，允许为 None，如果数据库中该字段为空，则返回 None
    spec: str | None = None
    quantity: int | None = None
    status: int | None = None  # 可选字段，允许为 None
