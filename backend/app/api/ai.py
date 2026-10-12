from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from services import ai_services, agent_services
from Schemas.ai import ChatRequest, ChatMessages
from model.user import User
from common.response import Response
from sqlalchemy.orm import Session
from database import get_db
import json
from fastapi.responses import StreamingResponse


router = APIRouter(prefix='/ai', tags=['模型调用接口'])

# 模型的调用都是post接口
@router.post('/chat')
async def chat(data: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """ 模型对话调用函数 """
    res = agent_services.run_agent(db, current_user, data)
    return Response.success(data=ChatMessages(role='assistant', content=res))


def _sse_line(payload: dict) -> str:
    """ 拼接 SSE 帧 固定格式：必须以data: 开头，再以\n\n进行分隔"""
    return f'data: {json.dumps(payload, ensure_ascii=False)}\n\n'

# 流式输出调用接口
@router.post('/chat/stream')
async def chat_stream(data: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """ 模型流式输出调用接口 """

    async def event_gen():
        """ 内层异步生成器：取出业务事件，包装成 SSE 文本再往外 yield"""
        async for event in agent_services.stream_agent(db, current_user, data):
            yield _sse_line(event)

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",  # 禁止任何缓存，保证每一条数据实时到达
            "Connection": "keep-alive",  # 保持长连接
            # 专治 Nginx 反向代理：Nginx 默认会把后端输出攒够一坨再转发，导致前端半天收不到字。这个响应头命令 Nginx 关闭缓冲、来一条转一条
            "X-Accel-Buffering": "no",
        },
    )
