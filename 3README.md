# Resumen del Proyecto Django en AWS

## Configuración del Entorno de Desarrollo (AWS y Django)

### 1. Instalación de dependencias
Usamos el archivo `requirements.txt` para instalar las dependencias necesarias para el proyecto (`dj-database-url`, `Django`, `cloudinary`, etc.).
También es recomendable usar un entorno virtual (`venv`) para aislar las dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuración y Arranque del Servidor
Usamos el siguiente comando para iniciar el servidor de desarrollo y que sea accesible externamente:

```bash
python manage.py runserver 0.0.0.0:8000
```
Esto asegura que el servidor escuche en todas las interfaces, permitiendo acceso desde la IP pública de AWS (ej. `http://52.47.166.127:8000`).

## Problemas y Soluciones Encontrados

### Error de CSRF (403 Forbidden)
**Problema**: Al intentar enviar formularios, aparecía el error "CSRF verification failed".
**Causa**: Falta de cookies necesarias o configuración de seguridad estricta (Secure Cookies) incompatible con pruebas HTTP.
**Solución**:
1.  Se añadieron los orígenes de confianza en `settings.py` (`CSRF_TRUSTED_ORIGINS`).
2.  Se desactivaron temporalmente `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` para permitir pruebas sin HTTPS.
3.  Se verificó la inclusión del tag `{% csrf_token %}` en los formularios POST.

### Problemas con HTTPS/SSL
**Problema**: Error de conexión al intentar acceder vía HTTPS o redirecciones infinitas.
**Solución**:
1.  Django solo sirve HTTP por defecto en modo desarrollo.
2.  Se desactivó `SECURE_SSL_REDIRECT = False` en `settings.py` para evitar forzar HTTPS durante las pruebas iniciales.

### Verificación de Conexión
Se logró acceso estable asegurándose de usar `http://` en lugar de `https://` y configurando `ALLOWED_HOSTS` correctamente (incluyendo la IP de EC2).

## Base de Datos y Autenticación
Los usuarios se registran en la base de datos default (SQLite `db.sqlite3` en este entorno de prueba).
*   **Persistencia**: Los usuarios permanecen guardados hasta ser eliminados manualmente.
*   **Gestión**: No se eliminan automáticamente. Se puede implementar lógica adicional o usar el panel de administración para gestionarlos.

## Errores y Advertencias
Durante el desarrollo se corrigieron errores de versiones de dependencias (downgrade de Django a 4.2.27 por compatibilidad) y configuraciones de `settings.py`.

---

# Django Project in AWS (Quick Start)

This project is a simple Django web application deployed on AWS EC2. It uses a database for storing user information and integrates with external services like Cloudinary.

## Setup Instructions

### 1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the development server:
```bash
python manage.py runserver 0.0.0.0:8000
```
Access the application at `http://<your-ec2-public-ip>:8000`.

## Troubleshooting

*   **CSRF Error (403 Forbidden)**: Ensure your browser accepts cookies and check for `{% csrf_token %}` in forms. Try using Incognito mode or clearing cookies if the error persists after upgrades.
*   **HTTPS Error**: The development server uses HTTP. Access via `http://`, not `https://`.

## User Management
Users are stored in the `auth_user` table. They persist until manually removed.
