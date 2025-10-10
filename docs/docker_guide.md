<div align="center">

**Language / Idioma:**
[🇺🇸 English](#table-of-contents) | [🇪🇸 Español](#tabla-de-contenidos)

</div>

---

# Docker, Docker Compose & Docker Hub Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Basic Concepts](#basic-concepts)
- [Essential Commands](#essential-commands)
- [Intermediate & Advanced Commands](#intermediate--advanced-commands)
- [Configuration Files](#configuration-files)
- [Best Practices](#best-practices)
- [Automation & CI/CD](#automation--cicd)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

---

## Introduction

Docker is a platform for containerizing applications, Docker Compose helps orchestrate multi-container setups, and Docker Hub is a cloud registry for images.

## Installation

### Docker

- Ubuntu/Debian:

```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

- macOS:

```bash
brew install --cask docker
```

- Windows:  
  Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)

### Docker Compose

- Linux:

```bash
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  docker-compose --version
```

- Included in Docker Desktop for Windows/macOS.

### Docker Hub

- Go to [hub.docker.com](https://hub.docker.com), sign up, and verify your email.

## Basic Concepts

- **Image**: Read-only template for containers.
- **Container**: Running instance of an image.
- **Service**: A container managed by Compose.
- **Network**: Communication channel between containers.
- **Volume**: Persistent data storage.

## Essential Commands

### Docker

- List images: `docker images`
- Run container: `docker run ubuntu:20.04`
- Interactive shell: `docker run -it ubuntu:20.04 /bin/bash`
- List running containers: `docker ps`
- Stop container: `docker stop <container_id>`
- Remove container: `docker rm <container_id>`
- Build image: `docker build -t my-app:latest .`
- Copy files: `docker cp file.txt container_id:/path/`

### Docker Compose

- Start services: `docker-compose up`
- Start in background: `docker-compose up -d`
- Stop services: `docker-compose down`
- View logs: `docker-compose logs`
- Execute command: `docker-compose exec web python manage.py migrate`
- Interactive shell: `docker-compose exec -it web /bin/bash`

### Docker Hub

- Login: `docker login`
- Tag image: `docker tag my-app:latest username/my-app:latest`
- Push image: `docker push username/my-app:latest`
- Pull image: `docker pull username/my-app:latest`

## Configuration Files

- **Dockerfile**: Instructions to build an image.
- **docker-compose.yml**: Multi-container configuration.
- **.dockerignore**: Files to exclude from build context.

## Best Practices

- Use specific image versions.
- Don’t run containers as root.
- Use `.dockerignore` to reduce build context.
- Use multi-stage builds for smaller images.
- Regularly scan images for vulnerabilities.
- Limit resources and use security options.

## Automation & CI/CD

Use GitHub Actions to build and push images to Docker Hub.
Example:

  ```yaml
  name: Build and Push
  on:
    push:
      branches: [main]
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v2
        - name: Build and push
          uses: docker/build-push-action@v2
          with:
            context: .
            push: true
            tags: username/my-app:latest
```

## Troubleshooting

- View logs: `docker logs <container>`
- Inspect container: `docker inspect <container>`
- Check Compose service status: `docker-compose ps`
- Debug service: `docker-compose exec web /bin/bash`
- Validate configuration: `docker-compose config --quiet`

## Intermediate & Advanced Commands

### Docker

- View detailed container info: `docker inspect <container_id>`
- Show container resource usage: `docker stats`
- Show container processes: `docker top <container_id>`
- Attach to a running container: `docker attach <container_id>`
- Commit changes to a new image: `docker commit <container_id> new_image_name`
- Export container filesystem: `docker export <container_id> > container.tar`
- Import a container filesystem: `docker import container.tar`
- Prune unused resources: `docker system prune`
- Remove all stopped containers: `docker container prune`
- Remove all unused images: `docker image prune -a`
- Run with resource limits: `docker run --memory=512m --cpus=1 ubuntu`
- Run with read-only filesystem: `docker run --read-only ubuntu`
- Set restart policy: `docker run --restart=always nginx`
- Create a named volume: `docker volume create mydata`
- Mount a named volume: `docker run -v mydata:/data ubuntu`
- Network inspect: `docker network inspect bridge`
- Connect a container to a network: `docker network connect <network> <container>`
- Disconnect a container from a network: `docker network disconnect <network> <container>`
- Build with build-args: `docker build --build-arg VAR=value .`
- Multi-stage build example: see Dockerfile section.

### Docker Compose

- List all services and their status: `docker-compose ps`
- Build images without starting containers: `docker-compose build`
- Rebuild images (no cache): `docker-compose build --no-cache`
- Pull latest images: `docker-compose pull`
- Push built images to registry: `docker-compose push`
- Restart all services: `docker-compose restart`
- Stop and remove all containers, networks, volumes, and images: `docker-compose down --rmi all --volumes --remove-orphans`
- Run a one-off command in a service: `docker-compose run --rm web python manage.py shell`
- Scale a service: `docker-compose up --scale web=3`
- Override configuration with another file: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up`
- View environment variables: `docker-compose config`
- Show full config (merged): `docker-compose config --resolve-image-digests`
- Remove orphaned containers: `docker-compose up --remove-orphans`
- Tail logs for a specific service: `docker-compose logs -f web`
- Execute a command as a different user: `docker-compose exec -u root web bash`
- Run in detached mode and build if needed: `docker-compose up -d --build`

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Docker Hub Docs](https://docs.docker.com/docker-hub/)

---

# Guía de Docker, Docker Compose y Docker Hub

## Tabla de Contenidos

- [Introducción](#introducción)
- [Instalación](#instalación)
- [Conceptos Básicos](#conceptos-básicos)
- [Comandos Esenciales](#comandos-esenciales)
- [Comandos Intermedios y Avanzados](#comandos-intermedios-y-avanzados)
- [Archivos de Configuración](#archivos-de-configuración)
- [Mejores Prácticas](#mejores-prácticas)
- [Automatización y CI/CD](#automatización-y-cicd)
- [Solución de Problemas](#solución-de-problemas)
- [Recursos](#recursos)

---

## Introducción

Docker es una plataforma para contenerizar aplicaciones, Docker Compose ayuda a orquestar configuraciones multi-contenedor y Docker Hub es un registro en la nube para imágenes.

## Instalación

### Docker

- Ubuntu/Debian:

```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

- macOS:

```bash
brew install --cask docker
```

- Windows:  
  Descarga Docker Desktop desde [docker.com](https://www.docker.com/products/docker-desktop)

### Docker Compose

- Linux:

```bash
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  docker-compose --version
```

- Incluido en Docker Desktop para Windows/macOS.

### Docker Hub

- Ve a [hub.docker.com](https://hub.docker.com), regístrate y verifica tu email.

## Conceptos Básicos

- **Imagen**: Plantilla de solo lectura para contenedores.
- **Contenedor**: Instancia en ejecución de una imagen.
- **Servicio**: Un contenedor gestionado por Compose.
- **Red**: Canal de comunicación entre contenedores.
- **Volumen**: Almacenamiento de datos persistente.

## Comandos Esenciales

### Docker

- Listar imágenes: `docker images`
- Ejecutar contenedor: `docker run ubuntu:20.04`
- Shell interactivo: `docker run -it ubuntu:20.04 /bin/bash`
- Listar contenedores en ejecución: `docker ps`
- Detener contenedor: `docker stop <container_id>`
- Eliminar contenedor: `docker rm <container_id>`
- Construir imagen: `docker build -t mi-app:latest .`
- Copiar archivos: `docker cp archivo.txt container_id:/ruta/`

### Docker Compose

- Iniciar servicios: `docker-compose up`
- Iniciar en segundo plano: `docker-compose up -d`
- Detener servicios: `docker-compose down`
- Ver logs: `docker-compose logs`
- Ejecutar comando: `docker-compose exec web python manage.py migrate`
- Shell interactivo: `docker-compose exec -it web /bin/bash`

### Docker Hub

- Iniciar sesión: `docker login`
- Etiquetar imagen: `docker tag mi-app:latest usuario/mi-app:latest`
- Subir imagen: `docker push usuario/mi-app:latest`
- Descargar imagen: `docker pull usuario/mi-app:latest`

## Archivos de Configuración

- **Dockerfile**: Instrucciones para construir una imagen.
- **docker-compose.yml**: Configuración multi-contenedor.
- **.dockerignore**: Archivos a excluir del contexto de build.

## Mejores Prácticas

- Usa versiones específicas de imágenes.
- No ejecutes contenedores como root.
- Usa `.dockerignore` para reducir el contexto de build.
- Usa builds multi-etapa para imágenes más pequeñas.
- Escanea imágenes regularmente por vulnerabilidades.
- Limita recursos y usa opciones de seguridad.

## Automatización y CI/CD

Usa GitHub Actions para construir y subir imágenes a Docker Hub.
Ejemplo:

```yaml
name: Build and Push
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push
        uses: docker/build-push-action@v2
        with:
          context: .
          push: true
          tags: usuario/mi-app:latest
```

## Solución de Problemas

- Ver logs: `docker logs <contenedor>`
- Inspeccionar contenedor: `docker inspect <contenedor>`
- Ver estado de servicios Compose: `docker-compose ps`
- Debuggear servicio: `docker-compose exec web /bin/bash`
- Validar configuración: `docker-compose config --quiet`

## Comandos Intermedios y Avanzados

### Docker

- Ver información detallada del contenedor: `docker inspect <container_id>`
- Mostrar uso de recursos del contenedor: `docker stats`
- Mostrar procesos del contenedor: `docker top <container_id>`
- Adjuntarse a un contenedor en ejecución: `docker attach <container_id>`
- Guardar cambios en una nueva imagen: `docker commit <container_id> nombre_nueva_imagen`
- Exportar el sistema de archivos de un contenedor: `docker export <container_id> > contenedor.tar`
- Importar un sistema de archivos de contenedor: `docker import contenedor.tar`
- Limpiar recursos no usados: `docker system prune`
- Eliminar todos los contenedores detenidos: `docker container prune`
- Eliminar todas las imágenes no usadas: `docker image prune -a`
- Ejecutar con límites de recursos: `docker run --memory=512m --cpus=1 ubuntu`
- Ejecutar con sistema de archivos de solo lectura: `docker run --read-only ubuntu`
- Establecer política de reinicio: `docker run --restart=always nginx`
- Crear un volumen nombrado: `docker volume create midatos`
- Montar un volumen nombrado: `docker run -v midatos:/data ubuntu`
- Inspeccionar red: `docker network inspect bridge`
- Conectar un contenedor a una red: `docker network connect <red> <contenedor>`
- Desconectar un contenedor de una red: `docker network disconnect <red> <contenedor>`
- Build con argumentos: `docker build --build-arg VAR=valor .`
- Ejemplo de build multi-etapa: ver sección Dockerfile.

### Docker Compose

- Listar todos los servicios y su estado: `docker-compose ps`
- Construir imágenes sin iniciar contenedores: `docker-compose build`
- Reconstruir imágenes (sin caché): `docker-compose build --no-cache`
- Descargar las últimas imágenes: `docker-compose pull`
- Subir imágenes construidas al registro: `docker-compose push`
- Reiniciar todos los servicios: `docker-compose restart`
- Detener y eliminar todos los contenedores, redes, volúmenes e imágenes: `docker-compose down --rmi all --volumes --remove-orphans`
- Ejecutar un comando puntual en un servicio: `docker-compose run --rm web python manage.py shell`
- Escalar un servicio: `docker-compose up --scale web=3`
- Sobrescribir configuración con otro archivo: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up`
- Ver variables de entorno: `docker-compose config`
- Mostrar configuración completa (fusionada): `docker-compose config --resolve-image-digests`
- Eliminar contenedores huérfanos: `docker-compose up --remove-orphans`
- Seguir logs de un servicio específico: `docker-compose logs -f web`
- Ejecutar un comando como otro usuario: `docker-compose exec -u root web bash`
- Ejecutar en modo detach y construir si es necesario: `docker-compose up -d --build`

## Resources

- [Documentación de Docker](https://docs.docker.com/)
- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [Documentación de Docker Hub](https://docs.docker.com/docker-hub/)

---
