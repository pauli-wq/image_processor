# 🖼️ Image Processor API

API REST asíncrona para la subida y procesamiento de imágenes en segundo plano, 
construida con **FastAPI** y **Celery**. Permite redimensionar imágenes y aplicar filtros 
(BLUR, SHARPEN, CONTOUR) de manera eficiente, delegando las tareas pesadas a workers en background

## ✨ Características

- **Subida asíncrona** de imágenes (JPEG, PNG, WebP, GIF).
- **Procesamiento en segundo plano** con Celery y Redis como broker.
- **Redimensionado** automático a 300×300 píxeles (miniatura).
- **Filtros**: `BLUR`, `SHARPEN`, `CONTOUR`.
- **Endpoints** para subir, consultar estado y obtener el resultado.
- **Validación** de tipo MIME, extensión y tamaño máximo de archivo.
- **Limpieza automática** de archivos temporales tras el éxito o fallo.

## 📦 Stack Tecnológico

|Componente        | Tecnología                |
| ---------------- | ------------------------- |
| Framework        | FastAPI                   |
| Cola de tareas   | Celery                    |
| Broker/Backend   | Redis                     |
| Procesamiento    | Pillow (PIL)              |

## Instalación

  ```bash
  # Clona el repositorio
  git clone https://github.com/pauli-wq/image_processor.git
  cd image_processor

  # Crea y activa un entorno virtual 
  python -m venv venv
  source venv/bin/activate   # Linux/macOS
  venv\Scripts\activate      # Windows

  # Instala las dependencias
  pip install -r requirements.txt
```

## Ejecución

Necesitas dos procesos: el servidor web y el worker de Celery.
  ```bash
  # Terminal 1: Inicia el servidor FastAPI
  uvicorn app.main:app --reload

  # Terminal 2: Inicia el worker de Celery
  celery -A app.celery_app worker --loglevel=info
  ```

# 📡 Endpoints 

#### `POST /upload` 
Sube una imagen para ser procesada y devuelve un task_id para seguir el progreso.
  ```json
  {
    "task_id": "a1b2c3d4e5f6789012345678",
    "message": "Image sent to processing queue"
  }
  ```

#### `GET /status/{task_id}`
  Devuelve el estado actual de la tarea.
  ```json
  {
    "task_id": "a1b2c3d4e5f6789012345678",
    "status": "PENDING"
  }
  ```

Posibles valores de `status`:
|-------------------------------------------------------|
|`PENDING`| La tarea está en cola, aún no se ha iniciado|
|`STARTED`| El worker ha comenzado a procesar la imagen|
|`SUCCESS`| El procesamiento se completó exitosamente|
|`FAILURE`| Ocurrió un error|
|-------------------------------------------------------|

#### `GET /result/{task_id}`
Devuelve el resultado final de la tarea. Incluye la URL de la imagen procesada cuando el estado es `SUCCESS`.

- `SUCCESS`:
  ```json
  {
    "task_id": "a1b2c3d4e5f6789012345678",
    "status": "SUCCESS",
    "processed_url": "/static/processed/a1b2c3d4e5f6789012345678.jpg",
    "error": null
  }
  ```
  
- `FAILURE`:
  ```json
  {
    "task_id": "a1b2c3d4e5f6789012345678",
    "status": "FAILURE",
    "processed_url": null,
    "error": "FileNotFoundError: El archivo temporal no existe"
  }
  ```

- `STARTED`:
  ```json
    {
      "task_id": "a1b2c3d4e5f6789012345678",
      "status": "STARTED",
      "processed_url": null,
      "error": null  
    }
  ```

# 🤝 Contribuciones
*Las contribuciones son bienvenidas.*
