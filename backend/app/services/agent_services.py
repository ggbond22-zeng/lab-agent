from sqlalchemy.orm import Session
from fastapi import Depends
from dependencies.auth import get_current_user
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from database import get_db
from langchain_openai import ChatOpenAI
from config import settings
from model.user import User
from common.exceptions import BusinessException
from services import agent_tools
from Schemas.ai import ChatRequest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from collections.abc import AsyncIterator
from typing import Any


SYSTEM_PROMPT = """你是智能实验室预约系统的 Agent，回答要简洁。
你可以：
1. 使用 search_docs 查询实验室的规则、安全、开放时间等问题
2. 使用 get_open_labs / get_lab_equipments  查询真实的实验室和设备
3. 再用户进行了预约确认后，使用 create_reservation 来进行真实的预约落库
4. 使用 get_today 来进行日期的换算

## 必须遵守
当用户提到了 今天、明天、后天 等日期相关的问题，请先调用 get_today 来获取日期，**不要直接返回 我需要确定明天的具体日期**。

在提交预约之前必须向用户复述：实验室ID与名称（或设备ID和名称）、日期、开始时间、结束时间。并得到用户确认再进行实际操作。
用户没说【确认】【确认预约】【就这样预约】等确定性回复之前，不要调用 create_reservation
工作流的确认环节里如果缺少了 lab_id，请先 get_open_labs 查到了 lab_id 再创建，不要瞎写。
工作流的确认环节里如果缺少了 equipment_id，请先 get_lab_equipments 查到了 equipment_id 再创建，不要瞎写。

预约成功后状态是待审核，必须管理员确认后实验室（或设备）才能使用。
不要瞎编数据库里没有的实验室或者设备信息。
如果是问开放时间或者实验室规则，优先调用 search_docs，不要凭空回复。
"""

TOOLS_LABELS = {
    "search_docs": "检索实验室知识库",
    "get_open_labs": "查询开放实验室",
    "get_lab_equipments": "查询实验室设备",
    "create_reservation": "创建预约单",
    "get_today": "获取今日日期"
}


def _build_history(data: ChatRequest):
    """ 构造历史会话 """
    # 构建历史会话
    history = []
    for message in data.messages:
        if message.role == 'user':
            history.append(HumanMessage(content=message.content.strip()))
        if message.role == 'assistant':
            history.append(AIMessage(content=message.content.strip()))
    if not history:
        raise BusinessException(message='请输入你对话内容')
    return history

def _tool_output_preview(output: Any, limit: int = 200) -> str:
    """ 裁剪工具信息 """
    if isinstance(output, ToolMessage):
        output = output.content
    text = output if isinstance(output, str) else str(output)
    return text if len(text) <= limit else text[:limit] + "..."

def _chunk_text(chunk: Any) -> str:
    """
    从模型流式 chunk 中扣出纯文本 
    content 有时是 str 有时候是 [{type:text},...] 也需要转成文本
    """
    if chunk is None:
        return ""
    # 安全取出chunk 中的 content
    content = getattr(chunk, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(part.get("text") or "")
            if isinstance(part, str):
                parts.append(part)
        return "".join(parts)
    return str(content) if content is not None else ""


async def stream_agent(db: Session, current_user: User, data: ChatRequest) -> AsyncIterator[dict]:
    """
    流式输出 边跑 Agent 边 yield 事件，供 SSE 推给前端
    提供给前端的事件类型：status / tool_start / tool_end / token / done / error
    注意：langgraph 1.x 已移除同步 stream_events(v2)，必须使用异步 astream_events(v2)，
    因此本函数是 async 生成器，接口层需要用 async for 消费
    """

    try:
        history = _build_history(data)
        agent = bulid_agent(db, current_user)
        # 构造输入信息
        input = {'messages':[SystemMessage(content=SYSTEM_PROMPT), *history]}

        # 先将模型开始进行思考的过程前的状态交给前端
        yield {"type": "status", "message": "正在思考..."}

        # 将问题交给agent进行思考回复，并得到graph图中的流程
        async for event in agent.astream_events(input, version='v2', config={"recursion_limit": 10}):
            # 获取当前节点事件
            kind = event.get("event")
            if kind == "on_tool_start":
                # 获取调用的工具名称
                name = event.get("name") or ""
                # 将信息交给前端
                yield {
                    "type": "tool_start",
                    "name": name,
                    "label": TOOLS_LABELS.get(name, name) # 如果得不到中文名称就返回原始英文名
                }

            # 图节点到调用工具结束
            elif kind == "on_tool_end":
                name = event.get("name") or ""
                yield {
                    # 事件的类型前后端要一致
                    "type": "tool_end",
                    "name": name,
                    "label": TOOLS_LABELS.get(name, name),
                    # 给前端预览信息，完整的信息仍在图内部的 messages 中使用
                    "preview": _tool_output_preview((event.get("data") or {}).get("output"))
                }

            # 图节点到agent整理全部信息将要进行输出
            elif kind == "on_chat_model_stream":
                # 只要agent节点的内容，其余的噪声内容全部过滤掉
                meta = event.get("metadata") or {}
                if meta.get("langgraph_node") not in (None, "agent"):
                    continue
                text = _chunk_text((event.get("data") or {}).get("chunk"))
                # 如果有文本就交给前端
                if text:
                    yield {
                        "type": "token",
                        "content": text
                    }

        # 流程图跑完后借出 done告知前端  此时不需要再返回content 在token中已经完整输出所有内容
        yield {"type": "done"}

    # 异常属于自定义异常
    except BusinessException as exc:
        # 流式输出也要使用 yield 抛出错误，使用 raise 返回json 会导致前端混乱
        yield {"type": "error", "message": exc.message}
    # 异常是自定义异常之外的
    except Exception:
        yield {"type": "error", "message": "大模型调用失败，请重试"}


def bulid_agent(db: Session, current_user: User):
    """ 构建agent """
    tools = agent_tools.build_tools(db, current_user)
    model = ChatOpenAI(
        model=settings.LLM_MODEL,
        base_url=settings.LLM_BASE_URL,
        api_key=settings.LLM_API_KEY,
        temperature=0,  # 因为是工具数据库中的内容进行回答的，不需要模型进行发散创作
        streaming=True
    ).bind_tools(tools)

    def agent_node(state: MessagesState):
        """
        构建agent 执行图(graph)
        langgraph 执行的工作流 节点
        """
        response = model.invoke(state['messages'])  # 得到全部的对话记录交给模型并得到回复
        return {'messages': [response]}  # 把新的回复内容追加到state中

    """
                ┌─────────────────────────────┐
                │                             │
                ▼                             │
    START ──► agent（LLM思考）──► 有 tool_call？──是──► tools（真正执行工具）
                ▲                             │            │
                │                             否           │
                │                             ▼            │
                └──────────────────────────── END ◄───结果带回agent
    """

    graph = StateGraph(MessagesState)  # 以消息状态作为运行流程图
    graph.add_node("agent", agent_node)   # 添加图节点，将消息内容作为节点，节点名称为agent
    graph.add_node(
        "tools", ToolNode(tools)
    )  #  ToolNode是框架的现成节点，读取模型刚说“我想调用 X 工具（参数 Y）"，真正执行 X(Y)，把结果以role=tool 的消息追加回状态。
    graph.add_edge(START, "agent")  # 添加 边，图的流程以agent 节点作为起点
    graph.add_conditional_edges(  # 添加 条件边(分岔路口) 当消息中出现 tool_calls 模型判断需要调用工具时，走该分支
        "agent", tools_condition  # tools_condition 是条件判断函数
    )
    graph.add_edge(
        "tools", "agent"
    )  # 再构建一条 工具调用结束后将得到的内容返回给agent，并添加到messages中作为上下文,让模型看着结果继续思考
    return graph.compile()   #  把图纸编译为可运行的应用

def run_agent(db: Session, current_user: User, data: ChatRequest):
    """ 运行agent """
    if not data.messages:
        raise BusinessException(message='当前对话内容为空')

    # 构建历史会话
    history = []
    for message in data.messages:
        if message.role == 'user':
            history.append(HumanMessage(content=message.content.strip()))
        if message.role == 'assistant':
            history.append(AIMessage(content=message.content.strip()))
    if not history:
        raise BusinessException(message='请输入你对话内容')

    # 创建agent
    agent = bulid_agent(db, current_user)

    # 进行对话
    try:
        result = agent.invoke(
            {
                'messages': [
                    SystemMessage(content=SYSTEM_PROMPT),
                    *history
                ]
            },
            config={'recursion_limit': 10}   # 对话循环上限是10轮
        )
    except BusinessException:
        raise
    except Exception:
        raise BusinessException(message='大模型调用失败，请重试')

    # 获得模型回复内容
    messages = result.get('messages') or []

    if not messages:
        raise BusinessException(message='大模型没有任何返回内容')

    # 优先得到模型最新回复的内容
    for message in reversed(messages):
        # 判断当前消息的类型是不是 AIMessage
        if isinstance(message, AIMessage) and message.content.strip():
            content = message.content.strip()
            # 如果得到的内容是列表类型的
            if isinstance(content, list):
                # 依次将content中的内容提取出来并拼接成字符串
                content = ''.join(patr.get('text', '') if isinstance(patr, dict) else str(patr) for patr in content)
            # 得到的是单条内容，以防万一先转成字符串
            if str(content).strip():
                return str(content).strip()
