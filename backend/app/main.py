from fastapi import FastAPI, logger
import uvicorn
from database import engine, Base
from model.user import User
from model.lab import Lab
from model.equipment import Equipment
from model.reservation import Reservation
from api import api
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from config import UPLOAD_DIR
from fastapi.staticfiles import StaticFiles
from common.exceptions import (
    BusinessException, 
    business_exception_hadler, 
    http_exception_hadler, 
    validation_exception_hadler,
    global_exception_hadler
)
import asyncio
from contextlib import asynccontextmanager
from services import reservation_service, kb_services

Base.metadata.create_all(bind=engine)  # 创建数据库表结构  在创建时，虽然代码中不会用到User类，但在创建数据库表结构时，
# SQLAlchemy会根据User类的定义来创建对应的数据库表。

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ 全局异步任务 """
    # 预热向量数据库
    try:
        await asyncio.to_thread(kb_services.warmup)  # to_thread 不会阻塞事件循环
    except Exception:
        logger.exception("向量数据库预热失败，服务继续启动")

    task = asyncio.create_task(reservation_service.run_expire_scan())  # 启动项目开启异步的扫描任务
    yield
    task.cancel()    # 关闭项目同时取消异步任务

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
	"http://127.0.0.1:5173",
	"https://ggbond22-zeng.github.io",   # GitHub Pages 线上前端地址
]

# 后端配置跨域，防止前端和后端的连接端口不一样导致在进行数据传输时出现错误
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的前端源，不要直接写 ["*"]
    allow_credentials=True,  # ✅ 关键：允许前端携带 Authorization token
    allow_methods=["*"],  # 允许所有请求方法 GET POST PUT DELETE OPTIONS
    allow_headers=["*"],  # 允许所有请求头（包含Authorization）
)

app.include_router(api)   # 让 app 包含 auth 中的所有 api 功能

# 注册异常处理
app.add_exception_handler(BusinessException, business_exception_hadler)
app.add_exception_handler(HTTPException, http_exception_hadler)
app.add_exception_handler(RequestValidationError, validation_exception_hadler)
app.add_exception_handler(Exception, global_exception_hadler)

# 挂载静态资源   在网页中访问链接： 本地IP/uploads/xxx.jpg
app.mount('/uploads', StaticFiles(directory=UPLOAD_DIR), name='uploads')


@app.get('/')
async def root():
    return {'message': '这是一个正在运行的FastAPI'}

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
