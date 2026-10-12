# 自定义异常处理和全局异常
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from common.response import Response
from fastapi.exceptions import RequestValidationError


class BusinessException(Exception):
    """ 自定义业务异常处理 """

    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(message)


async def business_exception_hadler(request: Request, exc: BusinessException):
    """ 自定义业务异常处理器 """

    return JSONResponse(
        status_code=200, # 这个状态码是服务器的状态码
        # content 中的是 api接口进行校验时，处理异常中的数据
        content=Response.error(code=exc.code, message=exc.message).model_dump() # JSONResponse 需要传入的数据类型是字典类型
    )


async def http_exception_hadler(request: Request, exc: HTTPException):
    """ http 异常处理器"""

    return JSONResponse(
        status_code=exc.status_code,  # 这个状态码是服务器的状态码
        # content 中的是 api接口进行校验时，处理异常中的数据
        content=Response.error(code=exc.status_code, message=exc.detail).model_dump(),
    )


async def validation_exception_hadler(request: Request, exc: RequestValidationError):
    """参数异常处理器"""

    return JSONResponse(
        status_code=422,  # 参数错误时的固定状态码
        content=Response.error(code=422, message='请求参数校验错误').model_dump(),
    )


async def global_exception_hadler(request: Request, exc: Exception):
    """全局异常处理器"""

    return JSONResponse(
        status_code=500,
        content=Response.error(code=500, message="服务器内部错误").model_dump(),
    )
