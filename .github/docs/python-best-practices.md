# 🐍 Buenas Prácticas para Proyectos Python

## **🎯 REGLAS FUNDAMENTALES**

### **Principios Core:**
- **PEP 8** como estándar de estilo obligatorio
- **Type hints** en todas las funciones públicas
- **Docstrings** en español para módulos, clases y funciones
- **Testing** con cobertura mínima del 80%
- **Logging estructurado** en lugar de prints

## **📁 Estructura de Proyecto Python**

### **Estructura recomendada:**
```
📁 backend/
├── 📄 main.py                    # Punto de entrada (FastAPI app)
├── 📄 requirements.txt           # Dependencias production
├── 📄 requirements-dev.txt       # Dependencias desarrollo
├── 📄 .env.example              # Template variables entorno
├── 📄 pyproject.toml            # Configuración proyecto moderno
├── 📁 src/
│   ├── 📄 __init__.py          # Marca como paquete Python
│   ├── 📁 api/                 # Endpoints y routers FastAPI
│   │   ├── 📄 __init__.py
│   │   ├── 📄 routes.py        # Rutas principales
│   │   └── 📄 dependencies.py  # Dependencias inyectables
│   ├── 📁 core/                # Configuración y constantes
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py        # Settings con Pydantic
│   │   └── 📄 exceptions.py    # Excepciones customizadas
│   ├── 📁 services/            # Lógica de negocio
│   │   ├── 📄 __init__.py
│   │   ├── 📄 pdf_service.py   # Procesamiento PDFs
│   │   ├── 📄 llm_service.py   # Integración Ollama
│   │   └── 📄 vector_service.py # FAISS operations
│   ├── 📁 models/              # Modelos Pydantic y schemas
│   │   ├── 📄 __init__.py
│   │   ├── 📄 requests.py      # Request models
│   │   └── 📄 responses.py     # Response models
│   └── 📁 utils/               # Utilidades y helpers
│       ├── 📄 __init__.py
│       ├── 📄 logger.py        # Configuración logging
│       └── 📄 helpers.py       # Funciones auxiliares
├── 📁 tests/                   # Tests con pytest
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py          # Fixtures compartidas
│   ├── 📁 unit/               # Tests unitarios
│   └── 📁 integration/        # Tests integración
├── 📁 storage/                 # Almacenamiento local
│   ├── 📁 uploads/
│   └── 📁 vectors/
└── 📁 logs/                    # Logs de aplicación
```

## **⚙️ Configuración de Herramientas**

### **pyproject.toml (Configuración moderna):**
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "rag-pdf-backend"
version = "1.0.0"
description = "Backend para sistema RAG con PDFs"
authors = [
    {name = "Tu Nombre", email = "tu@email.com"}
]
license = {text = "MIT"}
requires-python = ">=3.8"

[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # Directorios a excluir
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src"]

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/__pycache__/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:"
]
```

## **🔧 Herramientas de Calidad de Código**

### **requirements-dev.txt:**
```txt
# Herramientas de desarrollo
black==23.10.1              # Formateador de código
isort==5.12.0               # Organizador de imports
flake8==6.1.0               # Linter
mypy==1.6.1                 # Verificador de tipos
bandit==1.7.5               # Scanner de seguridad

# Testing
pytest==7.4.3              # Framework de testing
pytest-asyncio==0.21.1     # Tests async
pytest-cov==4.1.0          # Cobertura de tests
pytest-mock==3.12.0        # Mocking para tests
httpx==0.25.2              # Cliente HTTP para testing APIs

# Documentación
sphinx==7.2.6              # Generador documentación
sphinx-rtd-theme==1.3.0    # Tema para Sphinx
```

### **Scripts de calidad (Makefile o scripts/):**
```bash
# scripts/lint.sh
#!/bin/bash
echo "🔍 Ejecutando herramientas de calidad de código..."

echo "📏 Verificando formato con Black..."
black --check src/ tests/

echo "📦 Verificando imports con isort..."
isort --check-only src/ tests/

echo "🔧 Verificando estilo con Flake8..."
flake8 src/ tests/

echo "🔒 Verificando seguridad con Bandit..."
bandit -r src/

echo "📋 Verificando tipos con MyPy..."
mypy src/

echo "✅ Todas las verificaciones completadas!"
```

## **📝 Convenciones de Código**

### **Type Hints obligatorios:**
```python
from typing import List, Optional, Dict, Any
from pathlib import Path

def procesar_pdf(
    archivo_pdf: Path, 
    chunk_size: int = 1000
) -> List[str]:
    """
    Extrae y procesa texto de un archivo PDF.
    
    Args:
        archivo_pdf: Ruta al archivo PDF a procesar
        chunk_size: Tamaño de los chunks de texto
        
    Returns:
        Lista de chunks de texto extraídos
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el chunk_size es inválido
    """
    if not archivo_pdf.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {archivo_pdf}")
    
    # Implementación aquí...
    return []
```

### **Logging estructurado:**
```python
import logging
from loguru import logger

# Configuración de loguru (recomendado)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    backtrace=True,
    diagnose=True
)

# Uso correcto
def procesar_documento(documento_id: str) -> bool:
    """Procesa un documento específico."""
    logger.info(f"Iniciando procesamiento del documento: {documento_id}")
    
    try:
        # Lógica de procesamiento
        resultado = realizar_procesamiento(documento_id)
        logger.info(f"Documento {documento_id} procesado exitosamente")
        return resultado
    except Exception as e:
        logger.error(f"Error procesando documento {documento_id}: {str(e)}")
        raise
```

### **Manejo de configuración con Pydantic:**
```python
# src/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic."""
    
    # Servidor
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    
    # Storage
    upload_dir: str = "./storage/uploads"
    vector_store_dir: str = "./storage/vectors"
    
    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # CORS
    cors_origins: List[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instancia global
settings = Settings()
```

## **🧪 Testing con pytest**

### **Estructura de tests:**
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    """Cliente de pruebas para FastAPI."""
    return TestClient(app)

@pytest.fixture
def sample_pdf_path():
    """Ruta a un PDF de prueba."""
    return Path("tests/fixtures/sample.pdf")

# tests/unit/test_pdf_service.py
import pytest
from src.services.pdf_service import PDFService

class TestPDFService:
    """Tests para el servicio de procesamiento de PDFs."""
    
    def test_extraer_texto_pdf_valido(self, sample_pdf_path):
        """Debería extraer texto de un PDF válido."""
        service = PDFService()
        texto = service.extraer_texto(sample_pdf_path)
        
        assert isinstance(texto, str)
        assert len(texto) > 0
    
    def test_extraer_texto_archivo_inexistente(self):
        """Debería lanzar FileNotFoundError para archivo inexistente."""
        service = PDFService()
        
        with pytest.raises(FileNotFoundError):
            service.extraer_texto(Path("archivo_inexistente.pdf"))

# tests/integration/test_api.py
def test_upload_pdf_endpoint(client, sample_pdf_path):
    """Test de integración para endpoint de upload."""
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/api/upload-pdf",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    assert "document_id" in response.json()
```

## **🚨 Validación y Manejo de Errores**

### **Excepciones customizadas:**
```python
# src/core/exceptions.py
class RAGBaseException(Exception):
    """Excepción base para el sistema RAG."""
    pass

class DocumentProcessingError(RAGBaseException):
    """Error en el procesamiento de documentos."""
    pass

class LLMConnectionError(RAGBaseException):
    """Error de conexión con el LLM local."""
    pass

# Uso en servicios
def procesar_pdf(archivo: Path) -> str:
    """Procesa un archivo PDF y extrae su texto."""
    try:
        if not archivo.suffix.lower() == '.pdf':
            raise DocumentProcessingError(
                f"Formato de archivo no soportado: {archivo.suffix}"
            )
        
        # Procesamiento...
        return texto_extraido
    
    except Exception as e:
        logger.error(f"Error procesando PDF {archivo}: {str(e)}")
        raise DocumentProcessingError(f"No se pudo procesar el PDF: {str(e)}")
```

### **Validación con Pydantic:**
```python
# src/models/requests.py
from pydantic import BaseModel, validator, Field
from typing import Optional

class ChatRequest(BaseModel):
    """Modelo para requests de chat."""
    
    document_id: str = Field(..., min_length=1, description="ID del documento")
    question: str = Field(..., min_length=1, max_length=1000, description="Pregunta del usuario")
    max_tokens: Optional[int] = Field(None, ge=1, le=4000, description="Máximo de tokens")
    
    @validator('question')
    def question_no_empty(cls, v):
        """Valida que la pregunta no esté vacía."""
        if not v.strip():
            raise ValueError('La pregunta no puede estar vacía')
        return v.strip()
```

## **⚡ Optimizaciones de Rendimiento**

### **Async/await para operaciones I/O:**
```python
import asyncio
from typing import AsyncGenerator

async def procesar_documento_async(documento_path: Path) -> str:
    """Procesa documento de forma asíncrona."""
    # Operaciones I/O no bloqueantes
    texto = await extraer_texto_async(documento_path)
    embeddings = await generar_embeddings_async(texto)
    await guardar_vectores_async(embeddings)
    
    return "Procesamiento completado"

async def generar_respuesta_streaming(pregunta: str) -> AsyncGenerator[str, None]:
    """Genera respuesta en streaming para mejor UX."""
    async for chunk in ollama_client.chat_stream(pregunta):
        yield chunk
```

### **Caché inteligente:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def obtener_embeddings_cached(texto: str) -> List[float]:
    """Cachea embeddings para evitar recálculos."""
    # Solo cachear textos pequeños
    if len(texto) > 1000:
        return generar_embeddings_sin_cache(texto)
    
    return generar_embeddings(texto)
```

## **🔒 Seguridad**

### **Validación de archivos:**
```python
import magic
from pathlib import Path

def validar_archivo_seguro(archivo: Path) -> bool:
    """Valida que el archivo sea seguro para procesar."""
    
    # Validar extensión
    extensiones_permitidas = {'.pdf', '.txt', '.docx'}
    if archivo.suffix.lower() not in extensiones_permitidas:
        return False
    
    # Validar tipo MIME real
    tipo_mime = magic.from_file(str(archivo), mime=True)
    tipos_permitidos = {'application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
    
    return tipo_mime in tipos_permitidos
```

### **Sanitización de inputs:**
```python
import bleach
from html import escape

def sanitizar_texto(texto: str) -> str:
    """Sanitiza texto de entrada para prevenir XSS."""
    # Escapar HTML
    texto_escapado = escape(texto)
    
    # Limpiar con bleach
    texto_limpio = bleach.clean(texto_escapado, strip=True)
    
    return texto_limpio.strip()
```

## **📊 Monitoreo y Métricas**

### **Métricas de performance:**
```python
import time
from functools import wraps

def medir_tiempo(func):
    """Decorator para medir tiempo de ejecución."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        duracion = time.time() - inicio
        
        logger.info(f"{func.__name__} ejecutado en {duracion:.3f}s")
        return resultado
    
    return wrapper

@medir_tiempo
def procesar_documento_grande(documento: Path) -> str:
    """Procesa documento y mide performance."""
    # Implementación...
    pass
```

## **✅ Checklist de Calidad**

### **Antes de cada commit:**
- [ ] ✅ Tests pasan (pytest)
- [ ] ✅ Cobertura > 80% (pytest-cov)
- [ ] ✅ Formato correcto (black)
- [ ] ✅ Imports ordenados (isort)
- [ ] ✅ Sin errores de linting (flake8)
- [ ] ✅ Type hints correctos (mypy)
- [ ] ✅ Sin vulnerabilidades (bandit)
- [ ] ✅ Docstrings actualizados
- [ ] ✅ Variables de entorno documentadas

### **Comandos útiles:**
```bash
# Formatear código automáticamente
black src/ tests/
isort src/ tests/

# Ejecutar todos los tests con cobertura
pytest --cov=src --cov-report=html

# Verificar todo antes del commit
make lint  # o scripts/lint.sh

# Generar documentación
sphinx-build -b html docs/ docs/_build/
```

---

**💡 Recuerda:** El código se lee más veces de las que se escribe. Prioriza siempre la claridad y mantenibilidad sobre la cleverness.