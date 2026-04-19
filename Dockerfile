# Imagen base oficial de Python (versión ligera)
FROM python:3.11-slim

# Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar primero el requirements para aprovechar el caché de capas de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto en el que Flask escucha
EXPOSE 3000

# Variables de entorno con valores por defecto (serán sobreescritas al correr el contenedor)
ENV DB_HOST=localhost
ENV DB_USER=admin
ENV DB_PASSWORD=changeme
ENV DB_NAME=inventario_db
ENV DB_PORT=3306

# Comando para iniciar la aplicación
CMD ["python", "app.py"]
