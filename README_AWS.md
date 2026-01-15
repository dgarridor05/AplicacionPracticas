# Guía de Despliegue en AWS Elastic Beanstalk (Capa Gratuita)

Esta guía te ayudará a desplegar la aplicación "Relaciona" en AWS utilizando Elastic Beanstalk y Docker. Este método es compatible con la capa gratuita de AWS (Free Tier).

## Prerrequisitos

1.  **Cuenta de AWS**: Necesitas tener una cuenta creada en [aws.amazon.com](https://aws.amazon.com/).
2.  **AWS CLI EB CLI** (Recomendado): Instalar la herramienta de línea de comandos de Elastic Beanstalk.
    *   Instrucciones: [Instalar EB CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html)

## Opción 1: Despliegue usando la Consola Web de AWS (Más fácil visualmente)

1.  **Preparar el código**:
    *   Asegúrate de tener todos los archivos en un ZIP. Selecciona todos los archivos del proyecto (incluyendo `Dockerfile`, `requirements.txt`, carpeta `relaciona`, etc.) y comprímelos en `relaciona.zip`.

2.  **Crear la Aplicación en Elastic Beanstalk**:
    *   Ve a la consola de AWS y busca "Elastic Beanstalk".
    *   Haz clic en "Create Application" (Crear aplicación).
    *   **Nombre de la aplicación**: `relaciona-app`.
    *   **Plataforma**: Elige **Docker**.
        *   Platform branch: *Docker running on 64bit Amazon Linux 2023* (o la versión recomendada por defecto).
    *   **Código de la aplicación**:
        *   Selecciona "Upload your code" (Subir tu código).
        *   Sube el archivo `relaciona.zip` que creaste.
    *   **Configuración de Presets**: Elige "Single instance (Free Tier eligible)" para asegurarte de usar la capa gratuita.

3.  **Configurar Variables de Entorno (Opcional pero recomendado)**:
    *   Durante la creación (o después en Configuración > Software), añade las siguientes variables:
        *   `DEBUG`: `False`
        *   `SECRET_KEY`: (Genera una clave larga y segura)
        *   `ALLOWED_HOSTS`: `*` (o el dominio que te asigne AWS)

4.  **Lanzar**:
    *   Haz clic en "Create application". AWS tardará unos minutos en crear el entorno (EC2, Security Groups, Load Balancer, etc.).
    *   Una vez termine, verás una URL (ej. `http://relaciona-env.eba-xyz.us-east-1.elasticbeanstalk.com`). Haz clic para ver tu app.

## Opción 2: Despliegue usando EB CLI (Línea de comandos)

1.  Abre tu terminal en la carpeta del proyecto.
2.  Inicializa el proyecto EB:
    ```bash
    eb init -p docker relaciona-app
    ```
    (Sigue las instrucciones, selecciona tu región, ej. `us-east-1`).
3.  Crea el entorno y despliega:
    ```bash
    eb create relaciona-env
    ```
4.  Espera a que termine. Para abrir la app:
    ```bash
    eb open
    ```

## ⚠️ Nota Importante sobre la Base de Datos

Actualmente el proyecto usa **SQLite** (`db.sqlite3`).
*   **En Docker/Elastic Beanstalk, el sistema de archivos es efímero.**
*   Esto significa que si la aplicación se reinicia o haces un nuevo despliegue, **la base de datos se borrará y perderás los usuarios y datos creados**.
*   Para solucionar esto en producción, deberías conectar la app a una base de datos externa como **AWS RDS (PostgreSQL)**. AWS también ofrece una capa gratuita para RDS, pero requiere configuración adicional en `settings.py`.

## 🗄️ Configuración de Base de Datos (PostgreSQL)

Para conectar tu aplicación a una base de datos PostgreSQL (como AWS RDS), debes configurar las variables de entorno en Elastic Beanstalk (Configuration > Software).

Puedes usar una sola variable `DATABASE_URL` (recomendado) o variables individuales.

**Opción A: Usando DATABASE_URL (Recomendado)**

Formato: `postgres://USUARIO:CONTRASEÑA@HOST:PUERTO/NOMBRE_DB`

Ejemplo:
`DATABASE_URL`: `postgres://miusuario:mypassword@mi-rds-instance.aws-region.rds.amazonaws.com:5432/mi_db`

**Opción B: Variables Individuales**

*   `DB_NAME`: Nombre de la base de datos
*   `DB_USER`: Usuario
*   `DB_PASSWORD`: Contraseña
*   `DB_HOST`: Host (Endpoint de RDS)
*   `DB_PORT`: Puerto (por defecto 5432)

Recuerda asegurarte de que el **Security Group** de tu RDS permita el tráfico entrante desde el Security Group de tu instancia de Elastic Beanstalk en el puerto 5432.
