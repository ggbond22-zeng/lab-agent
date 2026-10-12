from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # 从当前目录往上2级


class Settings(BaseSettings):
    DATABASE_URL: str  # 读取.env 文件中的 DATABASE_URL 配置项
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
