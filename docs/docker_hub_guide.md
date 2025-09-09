# Docker Hub Guide

<div align="center">

**Language / Idioma:**
[🇺🇸 English](#docker-hub-guide) | [🇪🇸 Español](#guía-de-docker-hub)

</div>

---

## Docker Hub Guide

Docker Hub is a cloud-based registry service that allows you to store, manage, and distribute Docker images. It's the default registry for Docker and provides both public and private repositories.

## Getting Started

### Create Account
1. Go to [hub.docker.com](https://hub.docker.com)
2. Sign up for a free account
3. Verify your email address

### Login from Command Line
```bash
# Login to Docker Hub
docker login

# Login with specific username
docker login -u username

# Login to specific registry
docker login registry.docker.io
```

## Image Management

### Tagging Images
```bash
# Tag image for Docker Hub
docker tag my-app:latest username/my-app:latest

# Tag with version
docker tag my-app:latest username/my-app:1.0.0

# Tag with multiple tags
docker tag my-app:latest username/my-app:latest
docker tag my-app:latest username/my-app:1.0.0
docker tag my-app:latest username/my-app:stable
```

### Pushing Images
```bash
# Push image to Docker Hub
docker push username/my-app:latest

# Push all tags
docker push username/my-app --all-tags

# Push specific version
docker push username/my-app:1.0.0
```

### Pulling Images
```bash
# Pull latest image
docker pull username/my-app:latest

# Pull specific version
docker pull username/my-app:1.0.0

# Pull without tag (gets latest)
docker pull username/my-app
```

## Repository Management

### Create Repository
1. Go to Docker Hub dashboard
2. Click "Create Repository"
3. Choose repository name
4. Select visibility (Public/Private)
5. Add description and documentation

### Repository Settings
- **Visibility**: Public (free) or Private (paid)
- **Description**: Brief description of the image
- **Full Description**: Detailed documentation
- **Dockerfile**: Link to source code
- **Build Settings**: Automated builds

## Automated Builds

### Connect GitHub Repository
1. Go to repository settings
2. Click "Builds" tab
3. Click "Link to GitHub"
4. Authorize Docker Hub access
5. Select repository and branch

### Build Rules
```yaml
# .dockerignore
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.nyc_output
coverage
.nyc_output
.coverage
```

### Build Triggers
- **Push to branch**: Build on every push
- **Tag creation**: Build when tags are created
- **Pull request**: Build on pull requests (optional)

## Image Security

### Security Scanning
```bash
# Scan image for vulnerabilities
docker scan username/my-app:latest

# Scan with specific options
docker scan --file Dockerfile username/my-app:latest
```

### Best Practices
```dockerfile
# Use specific base image versions
FROM python:3.11.4-slim

# Don't run as root
RUN useradd --create-home app
USER app

# Use multi-stage builds
FROM node:18 AS builder
# ... build steps
FROM node:18-alpine
COPY --from=builder /app /app
```

## Organization Management

### Create Organization
1. Go to Docker Hub dashboard
2. Click "Create Organization"
3. Choose organization name
4. Add team members
5. Set permissions

### Team Management
- **Owner**: Full access to all repositories
- **Member**: Access to assigned repositories
- **Collaborator**: Limited access to specific repositories

## Webhooks and Integrations

### Webhook Configuration
```json
{
  "name": "deploy-webhook",
  "webhook_url": "https://api.example.com/webhook",
  "events": ["push", "delete"],
  "active": true
}
```

### CI/CD Integration
```yaml
# GitHub Actions example
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

## Advanced Features

### Image Signing
```bash
# Enable content trust
export DOCKER_CONTENT_TRUST=1

# Sign image
docker push username/my-app:latest

# Verify signature
docker trust inspect username/my-app:latest
```

### Rate Limits
- **Anonymous**: 100 pulls per 6 hours
- **Free account**: 200 pulls per 6 hours
- **Pro account**: 5000 pulls per day

### Private Repositories
```bash
# Pull private image
docker pull username/private-app:latest

# Push to private repository
docker push username/private-app:latest
```

## Troubleshooting

### Common Issues
```bash
# Authentication failed
docker logout
docker login

# Push denied
docker tag my-app:latest username/my-app:latest
docker push username/my-app:latest

# Pull failed
docker pull username/my-app:latest
```

### Performance Optimization
```bash
# Use specific tags instead of latest
docker pull username/my-app:1.0.0

# Use multi-stage builds for smaller images
# Use .dockerignore to reduce build context
```

## Best Practices

### Image Naming
- Use descriptive names
- Include version tags
- Use semantic versioning
- Tag stable releases

### Documentation
- Add clear descriptions
- Include usage examples
- Document environment variables
- Provide Dockerfile links

### Security
- Regular security scans
- Keep base images updated
- Use minimal base images
- Don't store secrets in images

---

## Guía de Docker Hub

Docker Hub es un servicio de registry basado en la nube que te permite almacenar, gestionar y distribuir imágenes Docker. Es el registry por defecto de Docker y proporciona repositorios tanto públicos como privados.

## Comenzar

### Crear Cuenta
1. Ve a [hub.docker.com](https://hub.docker.com)
2. Regístrate para una cuenta gratuita
3. Verifica tu dirección de email

### Iniciar Sesión desde Línea de Comandos
```bash
# Iniciar sesión en Docker Hub
docker login

# Iniciar sesión con nombre de usuario específico
docker login -u nombre_usuario

# Iniciar sesión en registry específico
docker login registry.docker.io
```

## Gestión de Imágenes

### Etiquetar Imágenes
```bash
# Etiquetar imagen para Docker Hub
docker tag mi-app:latest usuario/mi-app:latest

# Etiquetar con versión
docker tag mi-app:latest usuario/mi-app:1.0.0

# Etiquetar con múltiples etiquetas
docker tag mi-app:latest usuario/mi-app:latest
docker tag mi-app:latest usuario/mi-app:1.0.0
docker tag mi-app:latest usuario/mi-app:stable
```

### Subir Imágenes
```bash
# Subir imagen a Docker Hub
docker push usuario/mi-app:latest

# Subir todas las etiquetas
docker push usuario/mi-app --all-tags

# Subir versión específica
docker push usuario/mi-app:1.0.0
```

### Descargar Imágenes
```bash
# Descargar imagen más reciente
docker pull usuario/mi-app:latest

# Descargar versión específica
docker pull usuario/mi-app:1.0.0

# Descargar sin etiqueta (obtiene latest)
docker pull usuario/mi-app
```

## Gestión de Repositorios

### Crear Repositorio
1. Ve al dashboard de Docker Hub
2. Haz clic en "Create Repository"
3. Elige nombre del repositorio
4. Selecciona visibilidad (Público/Privado)
5. Añade descripción y documentación

### Configuración del Repositorio
- **Visibilidad**: Público (gratis) o Privado (de pago)
- **Descripción**: Breve descripción de la imagen
- **Descripción Completa**: Documentación detallada
- **Dockerfile**: Enlace al código fuente
- **Configuración de Build**: Builds automatizados

## Builds Automatizados

### Conectar Repositorio de GitHub
1. Ve a configuración del repositorio
2. Haz clic en pestaña "Builds"
3. Haz clic en "Link to GitHub"
4. Autoriza acceso de Docker Hub
5. Selecciona repositorio y rama

### Reglas de Build
```yaml
# .dockerignore
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.nyc_output
coverage
.nyc_output
.coverage
```

### Triggers de Build
- **Push a rama**: Build en cada push
- **Creación de tag**: Build cuando se crean tags
- **Pull request**: Build en pull requests (opcional)

## Seguridad de Imágenes

### Escaneo de Seguridad
```bash
# Escanear imagen por vulnerabilidades
docker scan usuario/mi-app:latest

# Escanear con opciones específicas
docker scan --file Dockerfile usuario/mi-app:latest
```

### Mejores Prácticas
```dockerfile
# Usar versiones específicas de imagen base
FROM python:3.11.4-slim

# No ejecutar como root
RUN useradd --create-home app
USER app

# Usar builds multi-etapa
FROM node:18 AS builder
# ... pasos de build
FROM node:18-alpine
COPY --from=builder /app /app
```

## Gestión de Organizaciones

### Crear Organización
1. Ve al dashboard de Docker Hub
2. Haz clic en "Create Organization"
3. Elige nombre de la organización
4. Añade miembros del equipo
5. Establece permisos

### Gestión de Equipos
- **Propietario**: Acceso completo a todos los repositorios
- **Miembro**: Acceso a repositorios asignados
- **Colaborador**: Acceso limitado a repositorios específicos

## Webhooks e Integraciones

### Configuración de Webhook
```json
{
  "name": "deploy-webhook",
  "webhook_url": "https://api.ejemplo.com/webhook",
  "events": ["push", "delete"],
  "active": true
}
```

### Integración CI/CD
```yaml
# Ejemplo de GitHub Actions
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

## Características Avanzadas

### Firma de Imágenes
```bash
# Habilitar content trust
export DOCKER_CONTENT_TRUST=1

# Firmar imagen
docker push usuario/mi-app:latest

# Verificar firma
docker trust inspect usuario/mi-app:latest
```

### Límites de Tasa
- **Anónimo**: 100 pulls por 6 horas
- **Cuenta gratuita**: 200 pulls por 6 horas
- **Cuenta Pro**: 5000 pulls por día

### Repositorios Privados
```bash
# Descargar imagen privada
docker pull usuario/app-privada:latest

# Subir a repositorio privado
docker push usuario/app-privada:latest
```

## Solución de Problemas

### Problemas Comunes
```bash
# Fallo de autenticación
docker logout
docker login

# Push denegado
docker tag mi-app:latest usuario/mi-app:latest
docker push usuario/mi-app:latest

# Pull falló
docker pull usuario/mi-app:latest
```

### Optimización de Rendimiento
```bash
# Usar etiquetas específicas en lugar de latest
docker pull usuario/mi-app:1.0.0

# Usar builds multi-etapa para imágenes más pequeñas
# Usar .dockerignore para reducir contexto de build
```

## Mejores Prácticas

### Nomenclatura de Imágenes
- Usar nombres descriptivos
- Incluir etiquetas de versión
- Usar versionado semántico
- Etiquetar releases estables

### Documentación
- Añadir descripciones claras
- Incluir ejemplos de uso
- Documentar variables de entorno
- Proporcionar enlaces a Dockerfile

### Seguridad
- Escaneos de seguridad regulares
- Mantener imágenes base actualizadas
- Usar imágenes base mínimas
- No almacenar secretos en imágenes
