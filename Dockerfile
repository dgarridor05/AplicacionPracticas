# Usar una imagen base oficial de Python ligera
FROM python:3.11-slim

# Establecer variables de entorno
# PYTHONDONTWRITEBYTECODE: Evita que Python escriba archivos pyc
# PYTHONUNBUFFERED: Asegura que los logs de Python se envíen directamente a la terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias
# libpq-dev es necesario para compilar psycopg2 (driver de PostgreSQL)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . /app/

# Ejecutar collectstatic para servir archivos estáticos (CSS, JS, IMGs)
# Se ejecuta durante el build para que estén listos
RUN python manage.py collectstatic --no-input

# Exponer el puerto en el que correrá la aplicación
EXPOSE 8000

# Comando para iniciar la aplicación usando Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "relaciona.wsgi:application"]
