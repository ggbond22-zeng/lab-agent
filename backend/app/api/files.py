import os
import time
import uuid
from pathlib import Path
import shutil
from Schemas.files import UploadRequest
from fastapi import APIRouter, UploadFile, File, Request
from common.exceptions import BusinessException
from common.response import Response
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_DIR, settings

router = APIRouter(prefix="/files", tags=["文件管理"])


@router.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    """文件存储管理"""
    # 1. 先判断文件名是否存在
    if not file.filename:
        raise BusinessException(message='文件名不能为空')

    # 2. 获取文件的原始上传名
    original_name = os.path.basename(file.filename)

    # 3. 获取文件的后缀
    ext = Path(original_name).suffix.lower()

    # 4. 判断该后缀是否符合定义的文件类型
    if ext not in ALLOWED_EXTENSIONS:
        raise BusinessException(message=f'当前不支持{ext}文件类型')

    # 5. 校验文件的大小
    if file.size and file.size > MAX_FILE_SIZE:
        raise BusinessException(message=f'文件大小不能超过 {MAX_FILE_SIZE // 1024 // 1024}MB')

    # 6. 构造文件保存时唯一的名字  由时间戳_uuid4.后缀 构成
    disk_name = f'{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}{ext}'

    # 7. 构造当前文件保存路径
    save_path = UPLOAD_DIR / disk_name

    # 8. 流式保存文件，防止一次性保存较大文件时出错
    with open(save_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    # 返回绝对 URL：云端部署时前端在另一个域名下，相对路径 /uploads/xxx 会 404
    # 优先用配置的 PUBLIC_BASE_URL（如 https://lab-agent.onrender.com），否则用请求自身的 base_url
    base_url = (settings.PUBLIC_BASE_URL or str(request.base_url)).rstrip('/')
    return Response.success(
        data=UploadRequest(
            original_name=original_name,
            disk_name=disk_name,
            size=file.size,
            url=f"{base_url}/uploads/{disk_name}",
        )
    )
