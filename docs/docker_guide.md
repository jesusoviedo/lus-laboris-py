# Docker Guide

<div align="center">

**Language / Idioma:**
[🇺🇸 English](#docker-guide) | [🇪🇸 Español](#guía-de-docker)

</div>

---

## Docker Guide

Docker is a platform that uses containerization to package applications and their dependencies into lightweight, portable containers. This guide covers Docker basics, best practices, and common commands.

## Installation

### Install Docker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# macOS (using Homebrew)
brew install --cask docker

# Windows
# Download Docker Desktop from https://www.docker.com/products/docker-desktop
```

### Verify Installation
```bash
docker --version
docker run hello-world
```

## Basic Concepts

### Images vs Containers
- **Image**: A read-only template with instructions for creating a container
- **Container**: A running instance of an image

### Dockerfile
A text file with instructions to build a Docker image.

## Essential Commands

### Image Management
```bash
# List images
docker images

# Pull an image
docker pull ubuntu:20.04

# Remove an image
docker rmi ubuntu:20.04

# Remove unused images
docker image prune

# Build an image
docker build -t my-app:latest .

# Build with specific Dockerfile
docker build -f Dockerfile.prod -t my-app:prod .
```

### Container Management
```bash
# Run a container
docker run ubuntu:20.04

# Run interactively
docker run -it ubuntu:20.04 /bin/bash

# Run in background (detached)
docker run -d nginx

# Run with port mapping
docker run -p 8080:80 nginx

# Run with volume mount
docker run -v /host/path:/container/path ubuntu

# Run with environment variables
docker run -e ENV_VAR=value ubuntu

# List running containers
docker ps

# List all containers
docker ps -a

# Stop a container
docker stop container_id

# Start a stopped container
docker start container_id

# Remove a container
docker rm container_id

# Remove all stopped containers
docker container prune
```

### Container Interaction
```bash
# Execute command in running container
docker exec -it container_id /bin/bash

# View container logs
docker logs container_id

# Follow logs in real-time
docker logs -f container_id

# Copy files to/from container
docker cp file.txt container_id:/path/to/destination
docker cp container_id:/path/to/file.txt ./
```

## Dockerfile Best Practices

### Basic Dockerfile Structure
```dockerfile
# Use official base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Set default command
CMD ["python", "app.py"]
```

### Multi-stage Builds
```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

## Docker Compose

### Basic docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
    volumes:
      - .:/app
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Docker Compose Commands
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs

# Execute command in service
docker-compose exec web python manage.py migrate
```

## Registry and Publishing

### Docker Hub
```bash
# Login to Docker Hub
docker login

# Tag image
docker tag my-app:latest username/my-app:latest

# Push to registry
docker push username/my-app:latest

# Pull from registry
docker pull username/my-app:latest
```

### Private Registry
```bash
# Run local registry
docker run -d -p 5000:5000 --name registry registry:2

# Tag for local registry
docker tag my-app:latest localhost:5000/my-app:latest

# Push to local registry
docker push localhost:5000/my-app:latest
```

## Security Best Practices

### Image Security
```dockerfile
# Use specific versions
FROM python:3.11.4-slim

# Don't run as root
RUN useradd --create-home app
USER app

# Use .dockerignore
# Add .dockerignore file to exclude unnecessary files
```

### Container Security
```bash
# Run with read-only filesystem
docker run --read-only ubuntu

# Limit resources
docker run --memory=512m --cpus=1 ubuntu

# Use security options
docker run --security-opt=no-new-privileges ubuntu
```

## Troubleshooting

### Common Issues
```bash
# Check container logs
docker logs container_name

# Inspect container
docker inspect container_name

# Check resource usage
docker stats

# Debug container
docker run -it --entrypoint /bin/bash image_name
```

### Performance Optimization
```bash
# Use .dockerignore to reduce build context
echo "node_modules" >> .dockerignore
echo ".git" >> .dockerignore

# Use multi-stage builds for smaller images
# Use alpine images when possible
FROM python:3.11-alpine

# Clean up in same RUN command
RUN apt-get update && apt-get install -y package && \
    rm -rf /var/lib/apt/lists/*
```

---

## Guía de Docker

Docker es una plataforma que usa containerización para empaquetar aplicaciones y sus dependencias en contenedores ligeros y portátiles. Esta guía cubre los conceptos básicos de Docker, mejores prácticas y comandos comunes.

## Instalación

### Instalar Docker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# macOS (usando Homebrew)
brew install --cask docker

# Windows
# Descargar Docker Desktop desde https://www.docker.com/products/docker-desktop
```

### Verificar Instalación
```bash
docker --version
docker run hello-world
```

## Conceptos Básicos

### Imágenes vs Contenedores
- **Imagen**: Una plantilla de solo lectura con instrucciones para crear un contenedor
- **Contenedor**: Una instancia en ejecución de una imagen

### Dockerfile
Un archivo de texto con instrucciones para construir una imagen Docker.

## Comandos Esenciales

### Gestión de Imágenes
```bash
# Listar imágenes
docker images

# Descargar una imagen
docker pull ubuntu:20.04

# Eliminar una imagen
docker rmi ubuntu:20.04

# Eliminar imágenes no utilizadas
docker image prune

# Construir una imagen
docker build -t mi-app:latest .

# Construir con Dockerfile específico
docker build -f Dockerfile.prod -t mi-app:prod .
```

### Gestión de Contenedores
```bash
# Ejecutar un contenedor
docker run ubuntu:20.04

# Ejecutar interactivamente
docker run -it ubuntu:20.04 /bin/bash

# Ejecutar en segundo plano (detached)
docker run -d nginx

# Ejecutar con mapeo de puertos
docker run -p 8080:80 nginx

# Ejecutar con montaje de volumen
docker run -v /ruta/host:/ruta/contenedor ubuntu

# Ejecutar con variables de entorno
docker run -e ENV_VAR=valor ubuntu

# Listar contenedores en ejecución
docker ps

# Listar todos los contenedores
docker ps -a

# Detener un contenedor
docker stop container_id

# Iniciar un contenedor detenido
docker start container_id

# Eliminar un contenedor
docker rm container_id

# Eliminar todos los contenedores detenidos
docker container prune
```

### Interacción con Contenedores
```bash
# Ejecutar comando en contenedor en ejecución
docker exec -it container_id /bin/bash

# Ver logs del contenedor
docker logs container_id

# Seguir logs en tiempo real
docker logs -f container_id

# Copiar archivos hacia/desde contenedor
docker cp archivo.txt container_id:/ruta/destino
docker cp container_id:/ruta/archivo.txt ./
```

## Mejores Prácticas de Dockerfile

### Estructura Básica de Dockerfile
```dockerfile
# Usar imagen base oficial
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para mejor caché)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash app
USER app

# Exponer puerto
EXPOSE 8000

# Establecer comando por defecto
CMD ["python", "app.py"]
```

### Builds Multi-etapa
```dockerfile
# Etapa de construcción
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Etapa de producción
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

## Docker Compose

### docker-compose.yml básico
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
    volumes:
      - .:/app
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Comandos de Docker Compose
```bash
# Iniciar servicios
docker-compose up

# Iniciar en segundo plano
docker-compose up -d

# Construir e iniciar
docker-compose up --build

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs

# Ejecutar comando en servicio
docker-compose exec web python manage.py migrate
```

## Registry y Publicación

### Docker Hub
```bash
# Iniciar sesión en Docker Hub
docker login

# Etiquetar imagen
docker tag mi-app:latest usuario/mi-app:latest

# Subir a registry
docker push usuario/mi-app:latest

# Descargar desde registry
docker pull usuario/mi-app:latest
```

### Registry Privado
```bash
# Ejecutar registry local
docker run -d -p 5000:5000 --name registry registry:2

# Etiquetar para registry local
docker tag mi-app:latest localhost:5000/mi-app:latest

# Subir a registry local
docker push localhost:5000/mi-app:latest
```

## Mejores Prácticas de Seguridad

### Seguridad de Imágenes
```dockerfile
# Usar versiones específicas
FROM python:3.11.4-slim

# No ejecutar como root
RUN useradd --create-home app
USER app

# Usar .dockerignore
# Agregar archivo .dockerignore para excluir archivos innecesarios
```

### Seguridad de Contenedores
```bash
# Ejecutar con sistema de archivos de solo lectura
docker run --read-only ubuntu

# Limitar recursos
docker run --memory=512m --cpus=1 ubuntu

# Usar opciones de seguridad
docker run --security-opt=no-new-privileges ubuntu
```

## Solución de Problemas

### Problemas Comunes
```bash
# Verificar logs del contenedor
docker logs nombre_contenedor

# Inspeccionar contenedor
docker inspect nombre_contenedor

# Verificar uso de recursos
docker stats

# Debuggear contenedor
docker run -it --entrypoint /bin/bash nombre_imagen
```

### Optimización de Rendimiento
```bash
# Usar .dockerignore para reducir contexto de build
echo "node_modules" >> .dockerignore
echo ".git" >> .dockerignore

# Usar builds multi-etapa para imágenes más pequeñas
# Usar imágenes alpine cuando sea posible
FROM python:3.11-alpine

# Limpiar en el mismo comando RUN
RUN apt-get update && apt-get install -y paquete && \
    rm -rf /var/lib/apt/lists/*
```
