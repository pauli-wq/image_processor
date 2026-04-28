from pydantic import BaseModel


class UploadResponse(BaseModel):
    task_id: str
    message: str = "Image sent to processing queue"


class TaskStatus(BaseModel):
    task_id: str
    status: str
    error: str | None = None


class TaskResult(BaseModel):
    task_id: str
    status: str
    processed_url: str | None = None
    error: str | None = None
