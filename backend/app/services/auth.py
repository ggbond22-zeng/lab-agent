from Schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from Schemas.user import UserResponse
from sqlalchemy.orm import Session
from model.user import User
from utils.password import verify_password, hash_password
from utils.jwt import create_access_token
from common.exceptions import BusinessException


def login(db: Session, data: LoginRequest):
    """处理用户登录请求，验证用户名和密码是否正确"""
    # 在数据库中查询User表，根据User表中的账号是否对应用户输入的账号进行查询，取唯一一条返回值
    user = db.query(User).filter(User.username == data.username).first()

    # 如果没有查找当相关账号，或密码输入不正确并且校验不通过时，抛出错误信息告知用户
    if not user or not verify_password(data.password, user.password):
        raise BusinessException(code=400, message="账号或密码错误")

    # 如果当前用户的 status 状态是 0 禁用状态，也会抛出错误信息
    if user.status != 1:
        raise BusinessException(code=400, message="当前账号被禁用")

    # 生成 jwt token
    token = create_access_token(user.id)

    # 返回得到的响应data数据
    return LoginResponse(token=token, user=UserResponse.model_validate(user))


def register(db: Session, data: RegisterRequest) -> None:
    """ 进行账号注册 """
    # 在数据库中查询User表，根据User表中的账号是否对应用户输入的账号进行查询，取唯一一条返回值
    user = db.query(User).filter(User.username == data.username).first()

    # 如果查询到了相关的用户数据，说明该账号已存在，抛出错误告知用户
    if user:
        raise BusinessException(message='账号已存在')

    # 将用户注册的账号信息保存在数据库中
    model_user = User(
        username = data.username,
        password = hash_password(data.password),    # 要将密码加密存储到数据库中
        name = data.name or data.username,   # 用户姓名可以默认是账号
        role = 'student',    # 注册的用户统一是学生
        status = 1
    )

    db.add(model_user)
    db.commit()    # 提交事务，数据才会真正写入数据库（commit 内部会自动 flush）
