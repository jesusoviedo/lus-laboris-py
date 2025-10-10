<div align="center">

**Language / Idioma:**
[🇺🇸 English](#github-actions-guide) | [🇪🇸 Español](#guía-de-github-actions)

</div>

---

## GitHub Actions Guide

GitHub Actions is a CI/CD platform that allows you to automate workflows directly in your GitHub repository. You can build, test, and deploy your code with custom workflows triggered by events like pushes, pull requests, or scheduled times.

## Getting Started

### Workflow Structure

```yaml
# .github/workflows/example.yml
name: Example Workflow

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest
```

## Triggers and Events

### Common Triggers

```yaml
on:
  # Push to specific branches
  push:
    branches: [ main, develop ]
    paths: [ 'src/**', 'tests/**' ]

  # Pull requests
  pull_request:
    branches: [ main ]
    types: [ opened, synchronize, reopened ]

  # Scheduled runs
  schedule:
    - cron: '0 2 * * 1'  # Every Monday at 2 AM

  # Manual trigger
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

  # Release creation
  release:
    types: [ published ]
```

### Path Filters

```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'package.json'
      - 'requirements.txt'
    paths-ignore:
      - 'docs/**'
      - '*.md'
```

## Jobs and Steps

### Basic Job Structure

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest --cov=src tests/

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Job Dependencies

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        run: pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build application
        run: docker build -t myapp .

  deploy:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: echo "Deploying..."
```

## Common Actions

### Checkout Code

```yaml
- name: Checkout code
  uses: actions/checkout@v3
  with:
    fetch-depth: 0  # Fetch all history
    token: ${{ secrets.GITHUB_TOKEN }}
```

### Setup Python

```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'  # Enable pip caching
```

### Setup Node.js

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v3
  with:
    node-version: '18'
    cache: 'npm'
```

### Docker Actions

```yaml
- name: Build Docker image
  uses: docker/build-push-action@v4
  with:
    context: .
    push: true
    tags: |
      myapp:latest
      myapp:${{ github.sha }}
```

### AWS Actions

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v2
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: Deploy to AWS
  run: |
    aws s3 sync dist/ s3://my-bucket/
```

## Environment Variables and Secrets

### Environment Variables

```yaml
env:
  NODE_ENV: production
  API_URL: https://api.example.com

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
    steps:
      - name: Build with environment
        run: |
          echo "Building for $NODE_ENV"
          echo "API URL: $API_URL"
```

### Secrets Management

```yaml
steps:
  - name: Use secret
    run: |
      echo "Secret value: ${{ secrets.MY_SECRET }}"
      # Never log secrets directly
      echo "Secret exists: ${{ secrets.MY_SECRET != '' }}"
```

## Matrix Strategy

### Python Matrix

```yaml
strategy:
  matrix:
    python-version: [3.9, 3.10, 3.11]
    os: [ubuntu-latest, windows-latest, macos-latest]
    exclude:
      - python-version: 3.9
        os: windows-latest
    include:
      - python-version: 3.12
        os: ubuntu-latest
        experimental: true
```

### Node.js Matrix

```yaml
strategy:
  matrix:
    node-version: [16, 18, 20]
    include:
      - node-version: 21
        experimental: true
```

## Conditional Execution

### Step Conditions

```yaml
steps:
  - name: Run on main branch
    if: github.ref == 'refs/heads/main'
    run: echo "Running on main"

  - name: Run on pull request
    if: github.event_name == 'pull_request'
    run: echo "Running on PR"

  - name: Run if previous step succeeded
    if: success()
    run: echo "Previous step succeeded"

  - name: Run if previous step failed
    if: failure()
    run: echo "Previous step failed"
```

### Job Conditions

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - name: Deploy
        run: echo "Deploying..."
```

## Caching

### Python Caching

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### Node.js Caching

```yaml
- name: Cache node modules
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

## Artifacts and Uploads

### Upload Artifacts

```yaml
- name: Build application
  run: |
    npm run build
    tar -czf dist.tar.gz dist/

- name: Upload build artifacts
  uses: actions/upload-artifact@v3
  with:
    name: build-files
    path: dist.tar.gz
    retention-days: 30
```

### Download Artifacts

```yaml
- name: Download build artifacts
  uses: actions/download-artifact@v3
  with:
    name: build-files
    path: ./dist
```

## Notifications

### Slack Notification

```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    channel: '#deployments'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

### Email Notification

```yaml
- name: Send email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: 'Deployment Status: ${{ job.status }}'
    body: 'Build completed with status: ${{ job.status }}'
    to: admin@example.com
  if: always()
```

## Best Practices

### Workflow Organization

```yaml
# Separate workflows for different purposes
# .github/workflows/ci.yml - Continuous Integration
# .github/workflows/cd.yml - Continuous Deployment
# .github/workflows/security.yml - Security scanning
```

### Security Best Practices

```yaml
# Use specific action versions
- uses: actions/checkout@v3  # Not @v1

# Use secrets for sensitive data
- name: Deploy
  run: |
    echo "Deploying with token: ${{ secrets.DEPLOY_TOKEN }}"

# Use least privilege
permissions:
  contents: read
  packages: write
```

### Performance Optimization

```yaml
# Use matrix for parallel jobs
strategy:
  matrix:
    python-version: [3.9, 3.10, 3.11]

# Use caching
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# Use appropriate runners
runs-on: ubuntu-latest  # Fastest for most cases
```

## Troubleshooting

### Common Issues

```yaml
# Debug workflow
- name: Debug information
  run: |
    echo "GitHub ref: ${{ github.ref }}"
    echo "GitHub event: ${{ github.event_name }}"
    echo "Runner OS: ${{ runner.os }}"
    echo "Working directory: ${{ github.workspace }}"
```

### Workflow Debugging

```yaml
# Enable debug logging
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

---

## Guía de GitHub Actions

GitHub Actions es una plataforma CI/CD que te permite automatizar flujos de trabajo directamente en tu repositorio de GitHub. Puedes construir, probar y desplegar tu código con flujos de trabajo personalizados activados por eventos como pushes, pull requests o horarios programados.

## Comenzar

### Estructura del Workflow

```yaml
# .github/workflows/ejemplo.yml
name: Ejemplo de Workflow

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Configurar Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Instalar dependencias
      run: |
        pip install -r requirements.txt

    - name: Ejecutar pruebas
      run: |
        pytest
```

## Triggers y Eventos

### Triggers Comunes

```yaml
on:
  # Push a ramas específicas
  push:
    branches: [ main, develop ]
    paths: [ 'src/**', 'tests/**' ]

  # Pull requests
  pull_request:
    branches: [ main ]
    types: [ opened, synchronize, reopened ]

  # Ejecuciones programadas
  schedule:
    - cron: '0 2 * * 1'  # Cada lunes a las 2 AM

  # Trigger manual
  workflow_dispatch:
    inputs:
      environment:
        description: 'Entorno para desplegar'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

  # Creación de release
  release:
    types: [ published ]
```

### Filtros de Ruta

```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'package.json'
      - 'requirements.txt'
    paths-ignore:
      - 'docs/**'
      - '*.md'
```

## Jobs y Steps

### Estructura Básica de Job

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - name: Checkout código
      uses: actions/checkout@v3

    - name: Configurar Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Instalar dependencias
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Ejecutar pruebas
      run: |
        pytest --cov=src tests/

    - name: Subir cobertura
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Dependencias de Jobs

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Ejecutar pruebas
        run: pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Construir aplicación
        run: docker build -t myapp .

  deploy:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Desplegar a producción
        run: echo "Desplegando..."
```

## Acciones Comunes

### Checkout de Código

```yaml
- name: Checkout código
  uses: actions/checkout@v3
  with:
    fetch-depth: 0  # Obtener todo el historial
    token: ${{ secrets.GITHUB_TOKEN }}
```

### Configurar Python

```yaml
- name: Configurar Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'  # Habilitar caché de pip
```

### Configurar Node.js

```yaml
- name: Configurar Node.js
  uses: actions/setup-node@v3
  with:
    node-version: '18'
    cache: 'npm'
```

### Acciones de Docker

```yaml
- name: Construir imagen Docker
  uses: docker/build-push-action@v4
  with:
    context: .
    push: true
    tags: |
      myapp:latest
      myapp:${{ github.sha }}
```

### Acciones de AWS

```yaml
- name: Configurar credenciales AWS
  uses: aws-actions/configure-aws-credentials@v2
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: Desplegar a AWS
  run: |
    aws s3 sync dist/ s3://mi-bucket/
```

## Variables de Entorno y Secretos

### Variables de Entorno

```yaml
env:
  NODE_ENV: production
  API_URL: https://api.ejemplo.com

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
    steps:
      - name: Construir con entorno
        run: |
          echo "Construyendo para $NODE_ENV"
          echo "API URL: $API_URL"
```

### Gestión de Secretos

```yaml
steps:
  - name: Usar secreto
    run: |
      echo "Valor secreto: ${{ secrets.MI_SECRETO }}"
      # Nunca logear secretos directamente
      echo "Secreto existe: ${{ secrets.MI_SECRETO != '' }}"
```

## Estrategia Matrix

### Matrix de Python

```yaml
strategy:
  matrix:
    python-version: [3.9, 3.10, 3.11]
    os: [ubuntu-latest, windows-latest, macos-latest]
    exclude:
      - python-version: 3.9
        os: windows-latest
    include:
      - python-version: 3.12
        os: ubuntu-latest
        experimental: true
```

### Matrix de Node.js

```yaml
strategy:
  matrix:
    node-version: [16, 18, 20]
    include:
      - node-version: 21
        experimental: true
```

## Ejecución Condicional

### Condiciones de Steps

```yaml
steps:
  - name: Ejecutar en rama main
    if: github.ref == 'refs/heads/main'
    run: echo "Ejecutando en main"

  - name: Ejecutar en pull request
    if: github.event_name == 'pull_request'
    run: echo "Ejecutando en PR"

  - name: Ejecutar si step anterior tuvo éxito
    if: success()
    run: echo "Step anterior tuvo éxito"

  - name: Ejecutar si step anterior falló
    if: failure()
    run: echo "Step anterior falló"
```

### Condiciones de Jobs

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - name: Desplegar
        run: echo "Desplegando..."
```

## Caché

### Caché de Python

```yaml
- name: Cachear dependencias pip
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### Caché de Node.js

```yaml
- name: Cachear node modules
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

## Artifacts y Subidas

### Subir Artifacts

```yaml
- name: Construir aplicación
  run: |
    npm run build
    tar -czf dist.tar.gz dist/

- name: Subir artifacts de build
  uses: actions/upload-artifact@v3
  with:
    name: archivos-build
    path: dist.tar.gz
    retention-days: 30
```

### Descargar Artifacts

```yaml
- name: Descargar artifacts de build
  uses: actions/download-artifact@v3
  with:
    name: archivos-build
    path: ./dist
```

## Notificaciones

### Notificación de Slack

```yaml
- name: Notificar Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    channel: '#deployments'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

### Notificación por Email

```yaml
- name: Enviar email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: 'Estado de Despliegue: ${{ job.status }}'
    body: 'Build completado con estado: ${{ job.status }}'
    to: admin@ejemplo.com
  if: always()
```

## Mejores Prácticas

### Organización de Workflows

```yaml
# Separar workflows para diferentes propósitos
# .github/workflows/ci.yml - Integración Continua
# .github/workflows/cd.yml - Despliegue Continuo
# .github/workflows/security.yml - Escaneo de seguridad
```

### Mejores Prácticas de Seguridad

```yaml
# Usar versiones específicas de acciones
- uses: actions/checkout@v3  # No @v1

# Usar secretos para datos sensibles
- name: Desplegar
  run: |
    echo "Desplegando con token: ${{ secrets.DEPLOY_TOKEN }}"

# Usar menor privilegio
permissions:
  contents: read
  packages: write
```

### Optimización de Rendimiento

```yaml
# Usar matrix para jobs paralelos
strategy:
  matrix:
    python-version: [3.9, 3.10, 3.11]

# Usar caché
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# Usar runners apropiados
runs-on: ubuntu-latest  # Más rápido para la mayoría de casos
```

## Solución de Problemas

### Problemas Comunes

```yaml
# Debuggear workflow
- name: Información de debug
  run: |
    echo "GitHub ref: ${{ github.ref }}"
    echo "GitHub event: ${{ github.event_name }}"
    echo "Runner OS: ${{ runner.os }}"
    echo "Directorio de trabajo: ${{ github.workspace }}"
```

### Debugging de Workflow

```yaml
# Habilitar logging de debug
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```
