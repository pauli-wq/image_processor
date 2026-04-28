import os 
import logging
from PIL import Image, ImageFilter
from app.celery_app import celery_app
from app.config.config import settings

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_image_task(
    self, 
    temp_path: str, 
    output_dir: str,
    filename: str,
    size: tuple,
    filter_type: str = None
):
    logger_info =(f"Processing Task {self.request.id}: {filename}")
    try:
        with open(temp_path) as img: 
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            
            # redimensionar manteniendo proporcion
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # aplicar filtro opcional
            if filter_type:
                filters = {
                    "BLUR": ImageFilter.BLUR,
                    "SHARPEN": ImageFilter.SHARPEN,
                    "CONTOUR": ImageFilter.CONTOUR
                }
            if f := filters.get(filter_type.upper()):
                img = img.filter(f)
                
            # guardamos
            out_path = os.path.join(output_dir, filename)
            img.save(out_path, quality=85, optimize=True)
                
                # limpiamos
            if os.path.exists(temp_path):
                    os.remove(temp_path)
            return {"filename": filename, "status": "success"}
    except Exception as exc:
        logger.error(f"PROCESSING ERROR {filename}: {exc}")
        # limpiamos en caso de error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise self.retry(exc=exc)