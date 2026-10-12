from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # 从当前目录往上2级


class Settings(BaseSettings):
    # 本地不配置时默认用 SQLite（云端在环境变量里注入真实连接串，会覆盖此默认值）
    DATABASE_URL: str = "sqlite+pysqlite:///./lab_agent.db"
    # 云端部署时的对外访问地址（如 https://lab-agent.onrender.com），用于拼接图片等静态资源的绝对 URL
    # 本地为空字符串时，上传接口会自动用请求的 base_url 拼接
    PUBLIC_BASE_URL: str = ""
    # 读取 .env 中的 jwt token 配置项
    JWT_SECRET_KEY: str
    JWT_EXPIRE_HOURS: int = 24
    JWT_ALGORITHM: str = "HS256"
    LLM_MODEL: str
    LLM_API_KEY: str
    LLM_BASE_URL: str

    # 配置并指定 .env 文件的路径和编码
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env",env_file_encoding='utf-8')


settings = Settings()

# 文件保存的根路径
UPLOAD_DIR = BASE_DIR / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)    # 如果文件夹没有创建时，自动创建文件夹

# 保存文件的最大大小
MAX_FILE_SIZE = 100 * 1024 * 1024   # 100MB  1024(kb) * 1024

# 保存文件的类型
ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".zip",
}
