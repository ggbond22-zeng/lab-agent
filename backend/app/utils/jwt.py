import jwt
from datetime import datetime, timedelta
from config import settings


def create_access_token(user_id: int):
    """ 创建 jwt token """
    # 创建 token 过期时间
    expire = datetime.now() + timedelta(hours=settings.JWT_EXPIRE_HOURS)

    # 创建 token 载荷
    payload = { 'user_id': user_id, 'exp': expire}   # key 'exp' 是固定写法，写成别的单词会报错

    # 构造token  使用jwt.encode 来进行编码创建token
    return jwt.encode(payload=payload, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token):
    """ 解析 jwt token """
    # 注意 在进行解析时，algorithm 是要加上s，并且传入的类型是列表类型
    # 解析得到的内容是 载荷 payload 中的内容
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
