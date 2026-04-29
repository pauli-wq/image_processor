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

| Componente       | Tecnología                |
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

## 📡 Referencia de la API

| Método | Endpoint            | Descripción                                                                 | Parámetros / Body                                     | Respuesta exitosa (ejemplo)                                                                                                                                                                                                                                                                                  |
|--------|---------------------|-----------------------------------------------------------------------------|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `POST` | `/upload`           | Sube una imagen para procesar en segundo plano.                             | **Form-data**<br>`file`: archivo de imagen (JPEG, PNG, WebP o GIF) | **202 Accepted**<br>```json<br>{<br>  "task_id": "a1b2c3d4e5f6789012345678",<br>  "message": "Image sent to processing queue"<br>}<br>```                                                                                                                             |
| `GET`  | `/status/{task_id}` | Consulta el estado actual de una tarea de procesamiento.                    | **Path**<br>`task_id`: UUID de la tarea               | **200 OK**<br>```json<br>{<br>  "task_id": "a1b2c3d4e5f6789012345678",<br>  "status": "PENDING"<br>}<br>```<br><br>Posibles valores de `status`: `PENDING`, `STARTED`, `SUCCESS`, `FAILURE`. Si `status` es `FAILURE`, se incluye el campo `error`.                                                   |
| `GET`  | `/result/{task_id}` | Obtiene el resultado final del procesamiento, incluyendo la URL de la imagen procesada. | **Path**<br>`task_id`: UUID de la tarea               | **200 OK** (éxito)<br>```json<br>{<br>  "task_id": "a1b2c3d4e5f6789012345678",<br>  "status": "SUCCESS",<br>  "processed_url": "/static/processed/a1b2c3d4e5f6789012345678.jpg",<br>  "error": null<br>}<br>```<br><br>**200 OK** (fallo)<br>```json<br>{<br>  "task_id": "a1b2c3d4e5f6789012345678",<br>  "status": "FAILURE",<br>  "processed_url": null,<br>  "error": "FileNotFoundError: ..."<br>}<br>``` |

> **Notas sobre errores comunes**  
> - `413` – El archivo excede el tamaño máximo permitido.  
> - `415` – Tipo de archivo no soportado.  
> - `500` – Error interno del servidor.
