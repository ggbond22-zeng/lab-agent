# 在登录成功后，如果想对用户的信息进行查询等操作，要先根据登录成功后的token进行鉴权，鉴权通过后，才能进行查询
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer  # 这是fastapi 官方提供的进行鉴权的依赖
from sqlalchemy.orm import Session
from database import get_db
from utils.jwt import decode_access_token
from model.user import User
from common.exceptions import BusinessException


# 先实例化鉴权依赖
oauth2_schema = OAuth2PasswordBearer(tokenUrl='/api/auth/login')  # 如果没有输入 token 是由其来返回错误

def get_current_user(token: str = Depends(oauth2_schema), db : Session = Depends(get_db)) -> User:
    """ jwt token 鉴权验证合法性 """
    # 先对token进行解析，如果对token进行解析失败，说明token的登录时效性已经过期
    try:
        payload = decode_access_token(token)
    except Exception:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='登录已过期，请重新登录')

    # 先获取到 user_id 
    user_id = payload.get('user_id')

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='无效的用户凭证')

    # 先查询用户账号对应的信息
    user = db.query(User).filter(User.id == user_id).first()

    if user.status != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='用户已被禁用')

    # 鉴权通过，返回用户信息
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """ 在 jwt token 鉴权的基础上，再进行管理员身份的验证"""
    if current_user.role != 'admin':
        raise BusinessException(message='无权访问', code=403)
    return current_user

    


