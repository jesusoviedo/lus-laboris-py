<div align="center">

**Language / Idioma:**
[🇺🇸 English](#fastapi-guide) | [🇪🇸 Español](#guía-fastapi)

</div>

---

## FastAPI Guide

This guide provides a comprehensive introduction to FastAPI, the web framework used in this project's API implementation. It covers the fundamentals, key concepts, and practical examples to help you understand FastAPI concepts and terminology before examining the project's API code in the `src/api/` directory.

**Note**: This guide focuses on FastAPI concepts and best practices in general, not on the specific implementation details of this project's API. Use this guide to familiarize yourself with FastAPI terminology and patterns, then explore the actual API code with this knowledge.

### What is FastAPI?

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It's designed to be easy to use and learn, fast to code, and ready for production.

### Key Features

- **High Performance**: One of the fastest Python frameworks available, comparable to NodeJS and Go
- **Fast to Code**: Increase development speed by 200-300%
- **Fewer Bugs**: Reduce developer-induced errors by 40%
- **Intuitive**: Great editor support with autocompletion everywhere
- **Easy**: Designed to be easy to use and learn
- **Short**: Minimize code duplication
- **Robust**: Get production-ready code with automatic interactive documentation

### Core Concepts

#### 1. Path Operations

Path operations are the main way to define API endpoints in FastAPI:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")  # Path operation decorator
def read_root():  # Path operation function
    return {"Hello": "World"}

@app.get("/items/{item_id}")  # Path parameter
def read_item(item_id: int):  # Type hints
    return {"item_id": item_id}
```

#### 2. Request Models (Pydantic)

FastAPI uses Pydantic models for data validation and serialization:

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.post("/items/")
def create_item(item: Item):  # Automatic validation
    return item
```

#### 3. Response Models

Define response structure and automatic documentation:

```python
class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    return {"id": item_id, "name": "Example", "price": 29.99}
```

#### 4. Dependency Injection

FastAPI's dependency system allows for clean separation of concerns:

```python
from fastapi import Depends

def get_db():
    # Database connection logic
    return database

@app.get("/items/")
def read_items(db = Depends(get_db)):
    return db.query(Items).all()
```

#### 5. Error Handling

Custom error responses and HTTP exceptions:

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
```

### Typical Project Structure

A well-organized FastAPI project typically follows this structure:

```
src/api/
├── main.py              # FastAPI application entry point
├── models/              # Pydantic models for request/response
├── routers/             # API route modules
├── dependencies/        # Dependency injection functions
├── services/            # Business logic layer
└── utils/               # Utility functions
```

### Common FastAPI Patterns

#### 1. CRUD API Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float

@app.post("/items/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    """Create a new item"""
    try:
        # Business logic here
        new_item = await item_service.create(item)
        return new_item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. Authentication with JWT

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"user": current_user}
```

#### 3. Async Database Operations

```python
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

@app.post("/users/")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Async database operation for better performance"""
    async with db:
        new_user = await user_service.create_user(db, user_data)
        await db.commit()
        await db.refresh(new_user)
    return new_user
```

### Environment Configuration

FastAPI applications typically use environment variables for configuration:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My FastAPI App"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "your-secret-key"
    
    class Config:
        env_file = ".env"

settings = Settings()
app = FastAPI(title=settings.app_name)
```

### Testing FastAPI Applications

#### 1. Unit Testing

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_item():
    response = client.post("/items/", json={"name": "Test", "price": 29.99})
    assert response.status_code == 200
    assert response.json()["name"] == "Test"
```

#### 2. Integration Testing

```python
def test_create_item():
    response = client.post("/items/", json={
        "name": "Test Item",
        "price": 29.99
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 29.99
```

### Deployment Considerations

#### 1. Production Server

```python
# main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2. Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. Environment Variables

```bash
# .env
DEBUG=false
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
API_V1_STR=/api/v1
```

### Best Practices

1. **Type Hints**: Always use type hints for better IDE support and validation
2. **Pydantic Models**: Use Pydantic models for request/response validation
3. **Async/Await**: Use async operations for I/O-bound tasks
4. **Error Handling**: Implement proper error handling with HTTPException
5. **Documentation**: Leverage FastAPI's automatic OpenAPI documentation
6. **Dependencies**: Use dependency injection for database connections and services
7. **Testing**: Write comprehensive tests for all endpoints
8. **Security**: Implement proper authentication and authorization

### Useful Resources

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Uvicorn ASGI Server](https://www.uvicorn.org/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

---

## Guía FastAPI

Esta guía proporciona una introducción completa a FastAPI, el framework web utilizado en la implementación de la API de este proyecto. Cubre los fundamentos, conceptos clave y ejemplos prácticos para ayudarte a entender los conceptos y terminología de FastAPI antes de examinar el código de la API del proyecto en el directorio `src/api/`.

**Nota**: Esta guía se enfoca en conceptos y mejores prácticas de FastAPI en general, no en los detalles específicos de implementación de la API de este proyecto. Usa esta guía para familiarizarte con la terminología y patrones de FastAPI, luego explora el código real de la API con este conocimiento.

### ¿Qué es FastAPI?

FastAPI es un framework web moderno y rápido (alto rendimiento) para construir APIs con Python 3.7+ basado en type hints estándar de Python. Está diseñado para ser fácil de usar y aprender, rápido para codificar, y listo para producción.

### Características Principales

- **Alto Rendimiento**: Uno de los frameworks Python más rápidos disponibles, comparable a NodeJS y Go
- **Rápido para Codificar**: Aumenta la velocidad de desarrollo en 200-300%
- **Menos Bugs**: Reduce errores inducidos por desarrolladores en 40%
- **Intuitivo**: Gran soporte de editor con autocompletado en todas partes
- **Fácil**: Diseñado para ser fácil de usar y aprender
- **Conciso**: Minimiza la duplicación de código
- **Robusto**: Obtén código listo para producción con documentación interactiva automática

### Conceptos Fundamentales

#### 1. Operaciones de Ruta

Las operaciones de ruta son la forma principal de definir endpoints de API en FastAPI:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")  # Decorador de operación de ruta
def read_root():  # Función de operación de ruta
    return {"Hello": "World"}

@app.get("/items/{item_id}")  # Parámetro de ruta
def read_item(item_id: int):  # Type hints
    return {"item_id": item_id}
```

#### 2. Modelos de Solicitud (Pydantic)

FastAPI usa modelos Pydantic para validación y serialización de datos:

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.post("/items/")
def create_item(item: Item):  # Validación automática
    return item
```

#### 3. Modelos de Respuesta

Define la estructura de respuesta y documentación automática:

```python
class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    return {"id": item_id, "name": "Example", "price": 29.99}
```

#### 4. Inyección de Dependencias

El sistema de dependencias de FastAPI permite una separación limpia de responsabilidades:

```python
from fastapi import Depends

def get_db():
    # Lógica de conexión a base de datos
    return database

@app.get("/items/")
def read_items(db = Depends(get_db)):
    return db.query(Items).all()
```

#### 5. Manejo de Errores

Respuestas de error personalizadas y excepciones HTTP:

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
```

### Estructura Típica del Proyecto

Un proyecto FastAPI bien organizado típicamente sigue esta estructura:

```
src/api/
├── main.py              # Punto de entrada de la aplicación FastAPI
├── models/              # Modelos Pydantic para request/response
├── routers/             # Módulos de rutas de API
├── dependencies/        # Funciones de inyección de dependencias
├── services/            # Capa de lógica de negocio
└── utils/               # Funciones utilitarias
```

### Patrones Comunes en FastAPI

#### 1. Ejemplo de API CRUD

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float

@app.post("/items/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    """Crear un nuevo elemento"""
    try:
        # Lógica de negocio aquí
        new_item = await item_service.create(item)
        return new_item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. Autenticación con JWT

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"user": current_user}
```

#### 3. Operaciones de Base de Datos Asíncronas

```python
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

@app.post("/users/")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Operación de base de datos asíncrona para mejor rendimiento"""
    async with db:
        new_user = await user_service.create_user(db, user_data)
        await db.commit()
        await db.refresh(new_user)
    return new_user
```

### Configuración de Entorno

Las aplicaciones FastAPI típicamente usan variables de entorno para configuración:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Mi App FastAPI"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "tu-clave-secreta"
    
    class Config:
        env_file = ".env"

settings = Settings()
app = FastAPI(title=settings.app_name)
```

### Pruebas de Aplicaciones FastAPI

#### 1. Pruebas Unitarias

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_item():
    response = client.post("/items/", json={"name": "Test", "price": 29.99})
    assert response.status_code == 200
    assert response.json()["name"] == "Test"
```

#### 2. Pruebas de Integración

```python
def test_create_item():
    response = client.post("/items/", json={
        "name": "Elemento de Prueba",
        "price": 29.99
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Elemento de Prueba"
    assert data["price"] == 29.99
```

### Consideraciones de Despliegue

#### 1. Servidor de Producción

```python
# main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2. Configuración Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. Variables de Entorno

```bash
# .env
DEBUG=false
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=tu-clave-secreta
API_V1_STR=/api/v1
```

### Mejores Prácticas

1. **Type Hints**: Siempre usa type hints para mejor soporte de IDE y validación
2. **Modelos Pydantic**: Usa modelos Pydantic para validación de request/response
3. **Async/Await**: Usa operaciones asíncronas para tareas ligadas a I/O
4. **Manejo de Errores**: Implementa manejo adecuado de errores con HTTPException
5. **Documentación**: Aprovecha la documentación automática OpenAPI de FastAPI
6. **Dependencias**: Usa inyección de dependencias para conexiones de base de datos y servicios
7. **Pruebas**: Escribe pruebas comprensivas para todos los endpoints
8. **Seguridad**: Implementa autenticación y autorización adecuadas

### Recursos Útiles

- [Documentación Oficial de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de Pydantic](https://pydantic-docs.helpmanual.io/)
- [Servidor ASGI Uvicorn](https://www.uvicorn.org/)
- [Tutorial de FastAPI](https://fastapi.tiangolo.com/tutorial/)
