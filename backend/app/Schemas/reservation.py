from pydantic import BaseModel, ConfigDict


class ReservationCreateRequest(BaseModel):
    """ 创建预约请求模型 """

    # 因为 user_id 在登录的用户中已经存在，不需要再从前端传入
    lab_id: int
    equipment_id: int | None = None
    date: str
    start_time: str
    end_time: str
    remark: str | None = None


class ReservationResponse(BaseModel):
    """
    预约响应信息模型 
    用以获取完整的预约人、预约实验室、预约设备等信息
    """

    id: int
    user_id: int
    user_name: str | None = None
    lab_id: int
    lab_name: str | None = None
    equipment_id: int | None = None
    equipment_name: str | None = None
    date: str
    start_time: str
    end_time: str
    type: str | None = None
    remark: str | None = None
    status: int

    # 允许 Pydantic 直接从对象的属性（而非字典的键）来读取数据并构造模型
    model_config = ConfigDict(from_attributes=True)

class AuditReservationRequest(BaseModel):
    """ 管理员审批预约信息请求模型 """
    status: int
