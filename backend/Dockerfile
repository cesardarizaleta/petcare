# Usar una imagen base ligera de Python
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema requeridas para psycopg2 y utilidades
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Recolectar archivos estáticos (Nginx de Dokploy los servirá si está configurado, 
# o se usarán a través de un middleware si se requiere, 
# pero aquí los generamos listos para producción)
RUN python manage.py collectstatic --noinput

# Exponer el puerto
EXPOSE 8000

# Ejecutar el servidor con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
