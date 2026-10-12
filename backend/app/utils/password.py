# 因为保存在数据库的密码要进行加密才能保证数据的安全，因此要对密码进行加密和登录时的校验
import bcrypt

def hash_password(password: str) -> str:
    """ 对密码进行hash加密 """
    # 使用 hashpw 后 将密码进行UTF-8编码，再使用 bcrypt.gensalt() 加盐提高随机性，最后将加密后的数据进行UTF-8编码，防止乱码
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hash_password: str) -> bool:
    """ 将前端传入的明文密码于后端加密后的密码进行校验 """
    # 两个密码都进行UTF-8编码，防止乱码,且 checkpw 的返回值是bool类型，校验成功返回True
    return bcrypt.checkpw(password.encode('utf-8'), hash_password.encode('utf-8'))

