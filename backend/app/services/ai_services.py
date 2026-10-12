from openai import OpenAI
from config import settings
from common.exceptions import BusinessException
from Schemas.ai import ChatMessages, ChatRequest
from services import kb_services, lab_service, equipment_service
from sqlalchemy.orm import Session
import json


SYSTEM_PROMPT = """你是智能实验室预约系统的助手，回答要简洁。
如果提供了相关资料，请根据相关资料的内容进行回答，不要胡乱编造资料内容中没有的信息。
需要查找实验室及实验室信息时，必须使用工具，根据工具调用得到的内容进行回答，工具调用得到的内容中没有的信息不要回答。
你不能替用户提交预约，也不能修改数据库。
如果用户要预约，请说明去「实验室列表」选择后提交，等待管理员审核。
如果用户问了跟实验室无关的问题，可以直接拒绝回答。
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_open_labs",
            "description": "查询处于开放状态的实验室列表，可以通过实验室名称和位置来进行搜索",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword":{
                        "type": "string",
                        "description":"实验室的名称或位置关键词，可以为空"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name": "get_lab_equipments",
            "description": "查询某个实验室的设备列表，可以通过设备名称来进行搜索",
            "parameters":{
                "type": "object",
                "properties":{
                    "keyword":{
                        "type":"string",
                        "description":"设备的名称，可以为空"
                    },
                    "lab_id":{
                        "type":"integer",
                        "desceiption":"实验室 ID"
                    }
                }
            }
        }
    }
]


def run_tool(db: Session, name: str, arguments: str):
    """ 调用工具 """
    # 先判断工具调用时填入的参数是否合法
    try:
        # 工具的参数信息是json格式
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return json.dumps({"error": '参数是不合法的json'}, ensure_ascii=False)

    try:
        if name == 'get_open_labs':
            # 查看是否有关键词查询
            keyword = (args.get('keyword') or "").strip() or None
            # 调用工具进行查询
            page = lab_service.get_Lab_list(db, page=1, page_size=10, keyword=keyword, status=1)
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

        if name == 'get_lab_equipments':
            # 获取实验室id并进行校验，lab_id 是必填的
            lab_id = args.get('lab_id')
            if not lab_id:
                return json.dumps({"error": '缺少实验室 id'}, ensure_ascii=False)

            keyword = (args.get('keyword') or '').strip() or None

            page = equipment_service.get_Equipment_list(db, page=1, page_size=10, keyword=keyword, lab_id=int(lab_id))

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

        return json.dumps({"error": f'未找到工具 {name}'}, ensure_ascii=False)

    except Exception as exc:
        return json.dumps({"error": exc.message}, ensure_ascii=False)


def get_client() -> OpenAI:
    """ 设置模型服务 """
    if not settings.LLM_API_KEY:
        raise BusinessException(message='未找到使用模型的API_KEY')

    return OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)


def chat(data: ChatRequest, db: Session):
    """ 模型聊天设置和上下文拼接 """
    if not data.messages:
        raise BusinessException(message='暂无对话信息')

    history = []
    for message in data.messages:
        # 将对话内容拼接到上下文中
        if message.role in ('user', 'assistant') and message.content.strip():
            # 因为此时的message 是json格式的，先将其转化为字典格式再添加到历史信息中
            history.append(message.model_dump())
    if not history:
        raise BusinessException(message='请输入您要对话的内容')

    # 获取用户最新输入的问题
    question = next((item['content'] for item in reversed(history) if item['role'] == 'user'), '')

    # 使用用户的问题进入向量数据库中进行查找
    knowleage = kb_services.search(question)

    system_prompt = SYSTEM_PROMPT

    # 如果向量数据库中查询到了相关内容，将其作为系统提示词的一部分
    if knowleage:
        system_prompt += '\n\n以下是查询得到的内容\n' + knowleage

    messages = [{'role': 'system', 'content': system_prompt},*history]

    client = get_client()

    try:
        # 第一次循环如果有工具调用得到的最后一条是role=tool，第二次循环如果不需要调用工具就让模型将工具调用得到的信息进行总结，否则继续循环
        for _ in range(3):
            # 创建会话
            res = client.chat.completions.create(
                model=settings.LLM_MODEL,
                # 传入的信息包括系统提示词和历史会话中（包括最新的会话）
                messages=messages,
                tools=TOOLS,
                tool_choice='auto'
            )
            msg = res.choices[0].message
            tool_calls = msg.tool_calls
            if not tool_calls:
                result = msg.content

                if not result.strip():
                    raise BusinessException(message='模型暂无返回内容')
                return result

            # 因为用的是LLM 不是 agent，模型只能知道该调用哪个模型，但是模型并不能主动调用模型，因此还需要手动调用
            messages.append({
                "role":"assistant",
                "content":msg.content or "",
                "tool_calls":[
                    {
                        "id": tool_call.id,
                        "type":"function",
                        "function":{
                            "name":tool_call.function.name,
                            "arguments":tool_call.function.arguments
                        }
                    } for tool_call in tool_calls
                ]
            })

            for tool_call in tool_calls:
                result = run_tool(db, tool_call.function.name, tool_call.function.arguments)
                messages.append({
                    "role": "tool", "content": result, "tool_call_id": tool_call.id
                })

        
    except Exception:
        raise BusinessException(message="模型对话调用失败，请稍后再进行尝试")
