from langchain_core.tools import tool
from sqlalchemy.orm import Session
from model.user import User
import json
from services import kb_services, lab_service, equipment_service, reservation_service
from Schemas.reservation import ReservationCreateRequest
from datetime import datetime
from common.exceptions import BusinessException


def build_tools(db: Session, current_user: User):
    """ 创建agent所需工具 """

    @tool
    def search_docs(query: str) -> str:
        """ 
        通过向量数据库检索知识库文档

        Args:
            query: 用户输入的问题
        """
        try:
            return kb_services.search(query) or '未找到相关内容'
        except Exception as exc:
            return json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False)

    @tool
    def get_open_labs(keywords: str) -> str:
        """
        查询开放状态下的实验室列表 

        Args:
            keywords: 实验室名称或位置关键词
        """
        try:
            keywords = keywords.strip() or None
            page = lab_service.get_Lab_list(
                db, page=1, page_size=10, keyword=keywords, status=1
            )
            # 该查询会将数据库中的数据全部查找到，我们只想返回特定字段给模型
            rows = [{
                "id": item.id,
                "name": item.name,
                "location": item.location,
                "capacity": item.capacity,
                "open_time": item.open_time,
                "close_time": item.close_time
            } for item in page.list]

            return json.dumps({"total": page.total, "labs": rows}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False)

    @tool
    def get_lab_equipments(
        lab_id: int,
        keywords: str = ''
    ) -> str:
        """
        获取某个实验室的设备列表

        Args:
            lab_id: 实验室 ID
            keywords: 设备名称
        """
        try:
            keywords = keywords.strip() or None
            page = equipment_service.get_Equipment_list(db, page=1, page_size=10, keyword=keywords, lab_id=int(lab_id))

            rows = [{
                "id": item.id,
                "name": item.name,
                "lab_id": item.lab_id,
                "lab_name": item.lab_name,
                "spec": item.spec,
                "quantity": item.quantity,
                "status": item.status
            } for item in page.list]

            return json.dumps({"total": page.total, "equipments": rows}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False)

    @tool
    def create_reservation(
        lab_id: int, 
        date: str, 
        start_time: str, 
        end_time: str, 
        equipment_id: int | None = None, 
        remark: str | None = None
    ) -> str:
        """
        创建预约信息预约实验室或设备

        Args:
            lab_id: 实验室ID
            date: 预约日期
            start_time: 开始时间
            end_time: 结束时间
            equipment_id: 设备ID
            remark: 预约备注
        """
        try:
            # 将传入的信息先进行校验
            data = ReservationCreateRequest(
                lab_id = lab_id,
                date = date,
                start_time = start_time,
                end_time = end_time,
                equipment_id = equipment_id,
                remark = remark
            )
            reservation_service.create_reservation(db, current_user, data)
            return json.dumps({
                "ok": True,
                'message': '预约创建成功，请等待管理器审批',
                "lab_id": lab_id,
                "equipment_id": equipment_id,
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
            }, ensure_ascii=False)
        except BusinessException as exc:
            return json.dumps({'ok': False, 'error': exc.message}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False)

    @tool
    def get_today() -> str:
        """ 获取服务器当前的日期 """
        now = datetime.now()
        return now.strftime('%Y-%m-%d')

    # 返回所有创建的工具
    return [search_docs, get_open_labs, get_lab_equipments, create_reservation, get_today]
