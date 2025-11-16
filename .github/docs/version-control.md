# 🔄 Gestión de Versiones

## **🌿 REGLA FUNDAMENTAL: SIEMPRE USAR RAMAS**

### **Flujo de trabajo obligatorio:**

1. **Al inicializar Git**: Crear rama `develop` como rama principal de trabajo
2. **Para cada nueva funcionalidad**: Crear rama específica desde `develop`
3. **Nunca trabajar directamente en `main`** - solo para releases estables

## **Comandos Git esenciales:**

### Inicialización del proyecto:
```bash
git init
git checkout -b develop
git add .
git commit -m "init: configuración inicial del proyecto"
```

### Para nueva funcionalidad:
```bash
git checkout develop
git pull origin develop  # Si trabajas en equipo
git checkout -b feature/descripcion-funcionalidad
# ... trabajo y commits ...
git checkout develop
git merge feature/descripcion-funcionalidad
git branch -d feature/descripcion-funcionalidad
```

## **Convención de nombres de ramas:**

- `feature/descripcion-funcionalidad` - Nuevas funcionalidades
- `fix/descripcion-error` - Corrección de errores
- `refactor/descripcion-mejora` - Refactorización de código
- `docs/descripcion-documentacion` - Actualizaciones de documentación
- `test/descripcion-pruebas` - Adición de pruebas

## **Mensajes de commit:**

### Formato estándar:
- Usar formato: `[tipo]: descripción en español`
- Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Ejemplos:
- `feat: agregar sistema de autenticación`
- `fix: corregir validación de formularios`
- `docs: actualizar README con instrucciones de instalación`
- `refactor: simplificar lógica de procesamiento de datos`
- `test: agregar pruebas unitarias para módulo de usuarios`
- `chore: actualizar dependencias del proyecto`

## **Control de cambios:**

### Buenas prácticas:
- Un commit por tarea completada
- Incluir archivos relacionados en el mismo commit
- Evitar commits con cambios no relacionados
- **SIEMPRE** crear nueva rama antes de implementar funcionalidades

### Revisión antes del commit:
- Verificar que no hay archivos temporales incluidos
- Revisar que los cambios sean coherentes
- Asegurar que el mensaje describe claramente lo realizado
- Comprobar que la funcionalidad esté completamente implementada

## **Gestión de releases:**

### Flujo de release:
```bash
# Crear rama de release desde develop
git checkout develop
git checkout -b release/v1.0.0

# Hacer ajustes finales y testing
# ...

# Merge a main para release
git checkout main
git merge release/v1.0.0
git tag v1.0.0

# Merge de vuelta a develop
git checkout develop
git merge release/v1.0.0

# Limpiar rama de release
git branch -d release/v1.0.0
```

### Versionado semántico:
- **MAJOR** (X.0.0): Cambios incompatibles en la API
- **MINOR** (0.X.0): Funcionalidades nuevas compatibles
- **PATCH** (0.0.X): Correcciones de errores compatibles