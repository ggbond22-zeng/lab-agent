# 对返回给前端的响应数据进行校验和格式化输出
from pydantic import BaseModel
from typing import Any



class Response(BaseModel):
    """ 对api接口的返回结果进行校验和结构化输出 """
    code: int
    message: str
    data: Any = None

    # 使用 @classmethod装饰器，可以在外部直接调用对应的类函数
    @classmethod
    # cls 表示 Response 类本身
    def success(cls, code: int = 200, message: str = '请求成功', data: Any = None):
        return cls(code=code, message=message, data=data)

    @classmethod
    def error(cls, code: int = 500, message: str = '请求失败'):
        return cls(code=code, message=message)


class PageListResponse(BaseModel):
    """ 分页列表内容校验 """
    list: Any = []
    total: int = 0


