from pydantic import BaseModel


class ChatMessages(BaseModel):
    """ 大模型对话信息校验模型 """
    role: str
    content: str

class ChatRequest(BaseModel):
    """ 大模型对话信息请求校验模型 """
    messages: list[ChatMessages]



