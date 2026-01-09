# Registro de Cambios - Fase 2: Despliegue y Base de Datos

Este documento resume las configuraciones avanzadas, correcciones de errores y la integración con servicios externos realizadas después de la configuración inicial.

## 1. Migración a Base de Datos Externa (Neon / PostgreSQL)
Para solucionar el problema de persistencia en Vercel (donde los datos se borraban al reiniciar), se configuró una base de datos PostgreSQL en la nube usando Neon.tech.

*   **Configuración en `settings.py`**:
    *   Se eliminó la base de datos `sqlite3` local para producción.
    *   Se implementó `dj_database_url` para leer automáticamente la variable de entorno `DATABASE_URL`.
*   **Gestión de Migraciones**:
    *   Se instaló el driver `psycopg2-binary`.
    *   Se ejecutaron las migraciones (`manage.py migrate`) remotamente contra la base de datos de Neon.
    *   Se cargaron los datos iniciales (`fixtures` y `quizzes_data.json`) en la nube.

## 2. Correcciones en Vercel (Debugging)
Se solucionaron múltiples problemas que impedían el arranque de la aplicación en Vercel:

*   **Error 500 (Crash)**: Se activó `DEBUG = True` temporalmente para identificar trazas de error.
*   **"Function Invocation Failed"**: Se detectó y corrigió un error de sintaxis (`IndentationError`) en el archivo `settings.py` que rompía la ejecución de Python.
*   **Descarga de archivo .py**: Se ajustó `vercel.json` para combinar la configuración "Legacy" (`builds`) con `routes`, asegurando que Vercel ejecute el código Python en lugar de servirlo como archivo descargable.
*   **Versión de Python**: Se forzó el uso de `python3.12` en `vercel.json`.

## 3. Soporte para Contenedores (Docker)
Para permitir el despliegue en plataformas como Northflank, Railway o cualquier servidor con Docker:

*   **`Dockerfile`**: Creado con Python 3.11-slim, instalación de dependencias y servidor Gunicorn configurado.
*   **`.dockerignore`**: Optimizado para excluir archivos innecesarios y reducir el peso de la imagen.

## Estado Actual
*   [x] Aplicación corriendo en Vercel.
*   [x] Base de datos persistente (Neon) conectada.
*   [x] Migraciones y datos de prueba cargados.
*   [x] Código listo para Docker.
*   [x] Configuración de `DEBUG` revertida para producción (seguridad).
