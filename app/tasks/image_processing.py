import os 
import logging
from pathlib import Path
from PIL import Image, ImageFilter
from app.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_image_task(self, temp_path: str, output_dir: str, filename: str, size: tuple, filter_type: str = None):
    logger.info(f"Iniciando procesamiento de {filename}")
    
    # Convertir a objetos Path para manejar rutas de forma segura
    p_temp = Path(temp_path)
    p_output = Path(output_dir)
    
    try:
        # 1. Verificar que el archivo existe antes de intentar abrirlo
        if not p_temp.exists():
            raise FileNotFoundError(f"El archivo temporal no existe: {temp_path}")

        # 2. Abrir la imagen con Pillow
        with Image.open(p_temp) as img:
            logger.info(f"Imagen abierta: {img.format}, {img.size}, {img.mode}")
            
            # Convertir a RGB si es necesario (JPEG no soporta transparencia)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            
            # 3. Redimensionar
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 4. Aplicar filtro opcional
            if filter_type:
                filters = {
                    "BLUR": ImageFilter.BLUR,
                    "SHARPEN": ImageFilter.SHARPEN,
                    "CONTOUR": ImageFilter.CONTOUR
                }
                if f := filters.get(filter_type.upper()):
                    img = img.filter(f)
            
            # 5. Guardar imagen procesada
            # Aseguramos que el directorio de salida exista
            p_output.mkdir(parents=True, exist_ok=True)
            
            out_path = p_output / filename
            img.save(out_path, quality=85, optimize=True)
            logger.info(f"Imagen guardada en: {out_path}")
            
            # 6. Limpieza: Borrar el archivo temporal original SOLO si todo salió bien
            if p_temp.exists():
                p_temp.unlink()
                
            return {"filename": filename, "status": "success"}
            
    except Exception as exc:
        logger.error(f"Error procesando {filename}: {exc}")
        
        # Intentar borrar el temporal si falló, para no dejar basura
        if p_temp.exists():
            try:
                p_temp.unlink()
            except:
                pass
                
        # Reintentar la tarea
        raise self.retry(exc=exc)