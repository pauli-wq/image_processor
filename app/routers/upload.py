import logging
import os
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, status
from app.celery_app import celery_app
from app.config.config import settings
from app.schemas.schemas import TaskResult, TaskStatus, UploadResponse
from app.tasks.image_processing import process_image_task

logger = logging.getLogger(__name__)
router = APIRouter(tags=["images"])

ALLOWED_MINE = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.post(
    "/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED
)
async def upload_image(file: UploadFile):
    # validar tipo MIME y extension
    content_type = file.content_type
    if content_type not in ALLOWED_MINE:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    ext = os.path.splitext(file.filename)[1].lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS.split(","):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    
    # leemos chunk por chunk para no saturar la RAM
    temp_filename = f"{uuid.uuid4().hex}.{ext}"
    temp_path = settings.UPLOAD_DIR / temp_filename
    
    try:
        file_size = 0
        with open(temp_path, "wb") as f: 
            while chunk := await file.read(1024 * 1024): # 1MB chunks
                file_size += len(chunk)
                if file_size > settings.MAX_FILE_SIZE:
                    raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE)
                f.write(chunk)
    except Exception as e: 
        if temp_path.exists():
            os.remove(temp_path)
        raise HTTPException(500, f"ERROR SAVING TEMPORARILY: {str(e)}")
    
    # enviamos a Celery
    task = process_image_task.delay(
        temp_path=str(temp_path),
        output_dir=str(settings.PROCESSED_DIR),
        temp_filename=temp_filename,
        size=(300, 300),
        filter_type=None
    )
    
    return UploadResponse(task_id=task.id)
    
    
@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    res = celery_app.AsyncResult(task_id)
    if res.status == "PENDING" and not res.result: 
        return TaskResult(task_id=task_id, status="UNKNOWN")
    return TaskResult(task_id=task_id, status=res.status)


@router.get("/result/{task_id}", response_model=TaskResult)
async def get_result(task_id: str):
    res = celery_app.AsyncResult(task_id)
    if res.status == "SUCCESS":
        result = res.result
        return TaskResult(
            task_id=task_id,
            status="SUCCESS",
            processed_url=f"{settings.STATIC_URL}/{result['filname']}"
        )
    elif res.status == "FAILURE":
        return TaskResult(task_id=task_id, status="FAILURE", error=str(res.result))
    return TaskResult(task_id=task_id, status=res.status) 
