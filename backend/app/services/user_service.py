from model.user import User
from operator import or_
from sqlalchemy.orm import Session
from common.response import PageListResponse
from utils.password import verify_password, hash_password
from common.exceptions import BusinessException
from Schemas.user import UserResponse, UpdateUserInfoRequest, UpdatePasswordRequest, CreateUserRequest


def get_user_info(user: User) -> UserResponse:
    """ 获取用户信息 """

    return UserResponse.model_validate(user)


def update_user_info(db: Session, user: User, data: UpdateUserInfoRequest):
    """ 修改用户个人信息 """
    # 因为 data 是经过pydantic校验后的数据，要先转成 dict 字典类型才能传入数据库中
    data_dict = data.model_dump(exclude_none=True, exclude={'role', 'status', 'password'})  # exclude_none=True 表示忽略为none 的字段
    for filed, value in data_dict.items():
        setattr(user, filed, value)   # 将 user 中对应的 filed(键) 修改为 value

    # 将修改后的信息提交到数据库中进行修改
    db.commit()
    db.refresh(user)

    # 返回的数据先进行校验
    return UserResponse.model_validate(user)

def update_password(db: Session, user: User, data: UpdatePasswordRequest):
    """ 修改用户密码 """
    # 先对用户输入的旧密码进行校验
    if not verify_password(data.old_password, user.password):
        raise BusinessException(message='旧密码输入错误')

    # 如果用户要修改的密码与之前的密码一致
    if data.new_password == data.old_password:
        raise BusinessException(message='新密码不能与旧密码一致')

    # 密码无误后将旧密码进行修改
    user.password = hash_password(data.new_password)
    db.commit()

def get_user_list(db: Session, page: int, page_size: int, keyword: str):
    """ 获取用户列表和分页信息 """
    query = db.query(User)

    # 先对用户输入的关键字进行模糊查询
    if keyword:
        query = query.filter(
            or_(User.username.ilike(f'%{keyword}%'), User.name.ilike(f'%{keyword}%'))
        )

    # 获取总页数
    total = query.count()
    # 分页查询  offset((page - 1) * page_size) 是查询的起始位置 limit(page_size) 是查询的条数
    items = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 因为items 是从 orm 中读取的数据类型，要先将其转换为 pydantic 类型 在 UserResponse 中进行校验
    return PageListResponse(list=[UserResponse.model_validate(item) for item in items], total=total)


def create_user(db: Session, data: CreateUserRequest):
    """创建用户"""
    # 先查询是否存在相同账号的用户
    exist = db.query(User).filter(User.username == data.username).first()
    if exist:
        raise BusinessException(message="该用户已存在")

    # 将数据添加到 orm 模型中
    user = User(
        username=data.username,
        password=hash_password(data.password),
        name=data.name,
        role=data.role,
        email=data.email,
        phone=data.phone,
        avatar=data.avatar,
        status=data.status,
    )

    # 添加到数据库中
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


def update_user(db: Session, user_id: int, data: UpdateUserInfoRequest):
    """更新用户"""
    # 先查询是否存在相同账号的用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BusinessException(message="未找到该用户")

    # 将数据解析为字典
    payload = data.model_dump(exclude_none=True)

    # 将前端输入的数据替换到后端的 orm 模型中
    for filter, value in payload.items():
        setattr(user, filter, value)

    # 提交到数据库中
    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)

def delete_user(db: Session, user_id: int, current_user: User):
    """删除用户"""
    if current_user.id == user_id:
        raise BusinessException(message='不能删除当前登录的用户')

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BusinessException(message='当前用户不存在')

    db.delete(user)
    db.commit()
