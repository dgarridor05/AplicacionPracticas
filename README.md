# Relaciona - Aplicación Django

Este proyecto ha sido configurado y optimizado para ejecutarse localmente y desplegarse tanto en **Render** como en **Vercel**.

## 📝 Cambios Realizados

A continuación se detallan las modificaciones técnicas implementadas para asegurar el funcionamiento del proyecto:

### 1. Configuración de Despliegue
*   **Render**:
    *   Creado archivo `render.yaml` para definición de servicio.
    *   Creado script `build.sh` para automatizar la instalación de dependencias, recolección de estáticos y migraciones.
*   **Vercel**:
    *   Creado `vercel.json` con configuración de runtime (Python 3.12).
    *   Ajustado `relaciona/wsgi.py` exponiendo la variable `app` para el entorno serverless.
    *   **Solución Base de Datos**: Se implementó una lógica en `settings.py` que detecta el entorno Vercel y copia la base de datos `db.sqlite3` a `/tmp/` (directorio temporal escribible) para evitar errores de "Read-only database".

### 2. Base de Datos
*   **Persistencia**: Se incluyó el archivo `db.sqlite3` en el control de versiones (Git) para garantizar que el despliegue tenga una estructura de datos inicial.
*   **Correcciones**: Se generaron y aplicaron migraciones faltantes para la tabla de perfiles de usuario (`accounts_userprofile`), solucionando errores 500 en el registro.

### 3. Limpieza y Mantenimiento
*   Eliminación de logs de error (`install_log.txt`) y archivos temporales (`__pycache__`).
*   Configuración depurada de `.gitignore`.
*   Restauración de dependencias críticas en `requirements.txt` (`psycopg2-binary`, `pillow`).

## 🚀 Cómo Ejecutar Localmente

Requisitos: Python 3.10+ instalado.

1.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Aplicar migraciones** (si es necesario):
    ```bash
    python manage.py migrate
    ```

3.  **Iniciar servidor**:
    ```bash
    python manage.py runserver
    ```
    Acceder en: `http://127.0.0.1:8000/`

## ⚠️ Notas Importantes sobre Vercel

Vercel es una plataforma *serverless* y su sistema de archivos es efímero (se reinicia) y de solo lectura.

*   **Persistencia de Datos**: Con la configuración actual (SQLite), **los datos nuevos (usuarios registrados, resultados) SE PERDERÁN** cada vez que Vercel reinicie el servidor o se haga un nuevo despliegue. La base de datos siempre volverá al estado inicial subido a Git.
*   **Recomendación**: Para un entorno de producción real donde se guarden los datos permanentemente, se debe conectar una base de datos externa (como PostgreSQL en Neon, Supabase o Render) usando la variable de entorno `DATABASE_URL`.
