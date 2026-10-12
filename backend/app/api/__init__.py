"""
注意：为什么只导入两个 router 不报错 ：FastAPI 只有在注册 声明了File /Form /UploadFile 参数
的接口时才检查这个依赖。auth 和 user 路由都没有文件上传，所以不触发检查；而 files.py 的/upload
接口用了 UploadFile = File(...) ，导入注册路由时立刻抛出 RuntimeError
此时需要 pip install python-multipart
"""

from fastapi import APIRouter
from api.auth import router as auth_router
from api.user import router as user_router
from api.files import router as files_router
from api.lab import router as lab_router
from api.equipment import router as equipment_router
from api.reservation import router as reservation_router
from api.ai import router as ai_router

api = APIRouter(prefix='/api')

api.include_router(auth_router)
api.include_router(user_router)
api.include_router(files_router)
api.include_router(lab_router)
api.include_router(equipment_router)
api.include_router(reservation_router)
api.include_router(ai_router)
