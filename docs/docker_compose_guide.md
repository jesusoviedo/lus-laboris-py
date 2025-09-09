# Docker Compose Guide

<div align="center">

**Language / Idioma:**
[🇺🇸 English](#docker-compose-guide) | [🇪🇸 Español](#guía-de-docker-compose)

</div>

---

## Docker Compose Guide

Docker Compose is a tool for defining and running multi-container Docker applications. It uses YAML files to configure application services, networks, and volumes, making it easy to manage complex applications with multiple components.

## Installation

Docker Compose is included with Docker Desktop. For Linux systems:

```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

## Basic Concepts

### Services
A service is a container that runs as part of your application.

### Networks
Services can communicate with each other through networks.

### Volumes
Persistent data storage that survives container restarts.

## Essential Commands

### Basic Operations
```bash
# Start services
docker-compose up

# Start in background (detached)
docker-compose up -d

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View running services
docker-compose ps

# View logs
docker-compose logs

# View logs for specific service
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f
```

### Service Management
```bash
# Start specific service
docker-compose up web

# Stop specific service
docker-compose stop web

# Restart specific service
docker-compose restart web

# Execute command in service
docker-compose exec web python manage.py migrate

# Execute interactive command
docker-compose exec -it web /bin/bash
```

## Configuration File Structure

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
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Advanced Configuration

### Environment Variables
```yaml
services:
  web:
    build: .
    environment:
      - NODE_ENV=production
      - API_KEY=${API_KEY}
    env_file:
      - .env
      - .env.local
```

### Volume Mounts
```yaml
services:
  web:
    build: .
    volumes:
      # Bind mount
      - ./src:/app/src
      # Named volume
      - app_data:/app/data
      # Anonymous volume
      - /app/tmp

volumes:
  app_data:
```

### Networks
```yaml
services:
  web:
    build: .
    networks:
      - frontend
      - backend

  db:
    image: postgres:13
    networks:
      - backend

networks:
  frontend:
  backend:
    driver: bridge
```

### Health Checks
```yaml
services:
  web:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Production Configuration

### Override Files
```yaml
# docker-compose.override.yml (for development)
version: '3.8'

services:
  web:
    volumes:
      - .:/app
    environment:
      - DEBUG=1
```

```yaml
# docker-compose.prod.yml (for production)
version: '3.8'

services:
  web:
    restart: unless-stopped
    environment:
      - DEBUG=0
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Using Override Files
```bash
# Use specific override file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

# Use environment-specific file
docker-compose --env-file .env.prod up
```

## Multi-Environment Setup

### Development Environment
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    ports:
      - "3000:3000"
      - "9229:9229"  # Debug port

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp_dev
    ports:
      - "5432:5432"
```

### Production Environment
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    ports:
      - "80:3000"

  db:
    image: postgres:13
    restart: unless-stopped
    environment:
      POSTGRES_DB: myapp_prod
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data

volumes:
  postgres_prod_data:
```

## Scaling Services

### Scale Services
```bash
# Scale web service to 3 instances
docker-compose up --scale web=3

# Scale multiple services
docker-compose up --scale web=3 --scale worker=2
```

### Load Balancing
```yaml
services:
  nginx:
    image: nginx
    ports:
      - "80:80"
    depends_on:
      - web

  web:
    build: .
    # No port mapping needed for internal communication
```

## Monitoring and Logging

### Log Configuration
```yaml
services:
  web:
    build: .
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Health Monitoring
```yaml
services:
  web:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Best Practices

### File Organization
```
project/
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .env
├── .env.example
└── services/
    ├── web/
    │   ├── Dockerfile
    │   └── src/
    └── db/
        └── init.sql
```

### Security Considerations
```yaml
services:
  web:
    build: .
    # Don't run as root
    user: "1000:1000"
    # Read-only filesystem
    read_only: true
    # Security options
    security_opt:
      - no-new-privileges:true
```

### Resource Management
```yaml
services:
  web:
    build: .
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Troubleshooting

### Common Issues
```bash
# Check service status
docker-compose ps

# View detailed logs
docker-compose logs --tail=100 web

# Debug service
docker-compose exec web /bin/bash

# Check service configuration
docker-compose config

# Validate configuration
docker-compose config --quiet
```

### Performance Optimization
```yaml
services:
  web:
    build: .
    # Use specific image tags
    image: myapp:1.0.0
    # Optimize layer caching
    build:
      context: .
      dockerfile: Dockerfile
      cache_from:
        - myapp:latest
```

---

## Guía de Docker Compose

Docker Compose es una herramienta para definir y ejecutar aplicaciones Docker multi-contenedor. Usa archivos YAML para configurar servicios de aplicación, redes y volúmenes, facilitando la gestión de aplicaciones complejas con múltiples componentes.

## Instalación

Docker Compose está incluido con Docker Desktop. Para sistemas Linux:

```bash
# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker-compose --version
```

## Conceptos Básicos

### Servicios
Un servicio es un contenedor que se ejecuta como parte de tu aplicación.

### Redes
Los servicios pueden comunicarse entre sí a través de redes.

### Volúmenes
Almacenamiento de datos persistente que sobrevive a los reinicios del contenedor.

## Comandos Esenciales

### Operaciones Básicas
```bash
# Iniciar servicios
docker-compose up

# Iniciar en segundo plano (detached)
docker-compose up -d

# Construir e iniciar
docker-compose up --build

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Ver servicios en ejecución
docker-compose ps

# Ver logs
docker-compose logs

# Ver logs de servicio específico
docker-compose logs web

# Seguir logs en tiempo real
docker-compose logs -f
```

### Gestión de Servicios
```bash
# Iniciar servicio específico
docker-compose up web

# Detener servicio específico
docker-compose stop web

# Reiniciar servicio específico
docker-compose restart web

# Ejecutar comando en servicio
docker-compose exec web python manage.py migrate

# Ejecutar comando interactivo
docker-compose exec -it web /bin/bash
```

## Estructura del Archivo de Configuración

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
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Configuración Avanzada

### Variables de Entorno
```yaml
services:
  web:
    build: .
    environment:
      - NODE_ENV=production
      - API_KEY=${API_KEY}
    env_file:
      - .env
      - .env.local
```

### Montajes de Volumen
```yaml
services:
  web:
    build: .
    volumes:
      # Montaje bind
      - ./src:/app/src
      # Volumen nombrado
      - app_data:/app/data
      # Volumen anónimo
      - /app/tmp

volumes:
  app_data:
```

### Redes
```yaml
services:
  web:
    build: .
    networks:
      - frontend
      - backend

  db:
    image: postgres:13
    networks:
      - backend

networks:
  frontend:
  backend:
    driver: bridge
```

### Health Checks
```yaml
services:
  web:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Configuración de Producción

### Archivos de Override
```yaml
# docker-compose.override.yml (para desarrollo)
version: '3.8'

services:
  web:
    volumes:
      - .:/app
    environment:
      - DEBUG=1
```

```yaml
# docker-compose.prod.yml (para producción)
version: '3.8'

services:
  web:
    restart: unless-stopped
    environment:
      - DEBUG=0
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Usar Archivos de Override
```bash
# Usar archivo de override específico
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

# Usar archivo específico del entorno
docker-compose --env-file .env.prod up
```

## Configuración Multi-Entorno

### Entorno de Desarrollo
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    ports:
      - "3000:3000"
      - "9229:9229"  # Puerto de debug

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp_dev
    ports:
      - "5432:5432"
```

### Entorno de Producción
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    ports:
      - "80:3000"

  db:
    image: postgres:13
    restart: unless-stopped
    environment:
      POSTGRES_DB: myapp_prod
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data

volumes:
  postgres_prod_data:
```

## Escalado de Servicios

### Escalar Servicios
```bash
# Escalar servicio web a 3 instancias
docker-compose up --scale web=3

# Escalar múltiples servicios
docker-compose up --scale web=3 --scale worker=2
```

### Balanceador de Carga
```yaml
services:
  nginx:
    image: nginx
    ports:
      - "80:80"
    depends_on:
      - web

  web:
    build: .
    # No se necesita mapeo de puertos para comunicación interna
```

## Monitoreo y Logging

### Configuración de Logs
```yaml
services:
  web:
    build: .
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Monitoreo de Salud
```yaml
services:
  web:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Mejores Prácticas

### Organización de Archivos
```
proyecto/
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .env
├── .env.example
└── services/
    ├── web/
    │   ├── Dockerfile
    │   └── src/
    └── db/
        └── init.sql
```

### Consideraciones de Seguridad
```yaml
services:
  web:
    build: .
    # No ejecutar como root
    user: "1000:1000"
    # Sistema de archivos de solo lectura
    read_only: true
    # Opciones de seguridad
    security_opt:
      - no-new-privileges:true
```

### Gestión de Recursos
```yaml
services:
  web:
    build: .
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Solución de Problemas

### Problemas Comunes
```bash
# Verificar estado de servicios
docker-compose ps

# Ver logs detallados
docker-compose logs --tail=100 web

# Debuggear servicio
docker-compose exec web /bin/bash

# Verificar configuración de servicio
docker-compose config

# Validar configuración
docker-compose config --quiet
```

### Optimización de Rendimiento
```yaml
services:
  web:
    build: .
    # Usar etiquetas de imagen específicas
    image: myapp:1.0.0
    # Optimizar caché de capas
    build:
      context: .
      dockerfile: Dockerfile
      cache_from:
        - myapp:latest
```
