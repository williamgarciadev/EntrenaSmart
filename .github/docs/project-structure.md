# 📁 Estructura de Proyecto Limpia

## **🚨 REGLA FUNDAMENTAL: RAÍZ LIMPIA**
**Solo mantener en la raíz del proyecto archivos esenciales:**

### ✅ **Archivos permitidos en raíz:**
```
📁 nombre-proyecto/
├── 📄 main.py|index.js|app.py      # Punto de entrada principal
├── 📄 requirements.txt|package.json # Dependencias
├── 📄 .env.example                 # Template de configuración
├── 📄 .gitignore                   # Control de versiones
├── 📄 README.md                    # Documentación principal
├── 📁 src/|backend/                # Código principal organizado
├── 📁 scripts/                     # Scripts utilitarios organizados
├── 📁 config/                      # Configuraciones específicas
├── 📁 output/                      # Resultados generados
├── 📁 tasks/                       # Planificación y documentación
└── 📁 docs/                        # Documentación adicional
```

### ❌ **Evitar en raíz:**
- Scripts sueltos de prueba (`test_algo.py`, `prueba_*.js`)
- Archivos de configuración específicos (`config_database.py`)
- Scripts de análisis (`analyze_*.py`, `extraer_*.py`)
- Archivos temporales o de prueba
- JSONs de salida o datos procesados

## **📂 Organización recomendada:**

### Scripts por funcionalidad:
```
📁 scripts/
├── 📁 database/
│   ├── config_database.py
│   └── test_connection.py
├── 📁 analysis/
│   ├── analyze_patterns.py
│   └── process_data.py
├── 📁 automation/
│   ├── deploy_script.py
│   └── backup_system.py
└── 📁 utils/
    ├── helpers.py
    └── validators.py
```

### Código principal organizado:
```
📁 src/
├── 📁 presentation/     # Controllers, API endpoints
├── 📁 business/         # Lógica de negocio
├── 📁 data/            # Acceso a datos, repositorios
├── 📁 infrastructure/   # Servicios externos, configuración
└── 📁 shared/          # Utilidades comunes
```

### Configuraciones por ambiente:
```
📁 config/
├── 📄 development.env
├── 📄 testing.env
├── 📄 production.env
└── 📄 base_config.py
```

### Documentación estructurada:
```
📁 docs/
├── 📄 architecture.md
├── 📄 api-reference.md
├── 📄 deployment.md
└── 📁 images/
```

## **🧹 Limpieza automática:**

### Antes de cada commit:
- Revisar que la raíz esté limpia
- Mover archivos sueltos a directorios apropiados
- Eliminar archivos temporales o de prueba
- Actualizar .gitignore según sea necesario

### Buenas prácticas:
- Hacer backup de configuraciones importantes antes de modificar
- Organizar scripts por funcionalidad en subdirectorios apropiados
- Mantener estructura limpia en `output/` para resultados
- Crear directorio `tasks/` si no existe para documentar planes