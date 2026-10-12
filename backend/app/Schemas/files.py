from pydantic import BaseModel

class UploadRequest(BaseModel):
    original_name: str
    disk_name: str
    size: int
    url: str
