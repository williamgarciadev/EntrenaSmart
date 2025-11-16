# 🏗️ Principios SOLID y Código Limpio

## **Principios SOLID**

### **S - Single Responsibility Principle (Responsabilidad Única)**
- Cada clase o función debe tener una sola razón para cambiar
- Una función = una responsabilidad específica
- Ejemplo: `validar_email()`, `enviar_notificacion()`, `calcular_precio()`

### **O - Open/Closed Principle (Abierto/Cerrado)**
- Abierto para extensión, cerrado para modificación
- Usar interfaces, herencia o composición para agregar funcionalidad
- Evitar modificar código existente cuando se agreguen características

### **L - Liskov Substitution Principle (Sustitución de Liskov)**
- Los objetos derivados deben poder reemplazar a sus objetos base
- Las subclases deben mantener el comportamiento esperado de la clase padre
- Ejemplo: Si `Animal` tiene método `mover()`, `Perro` debe implementarlo correctamente

### **I - Interface Segregation Principle (Segregación de Interfaces)**
- Los clientes no deben depender de interfaces que no usan
- Crear interfaces específicas y pequeñas en lugar de una grande
- Mejor múltiples interfaces especializadas que una general

### **D - Dependency Inversion Principle (Inversión de Dependencias)**
- Depender de abstracciones, no de implementaciones concretas
- Los módulos de alto nivel no deben depender de módulos de bajo nivel
- Usar inyección de dependencias cuando sea posible

## **Código Limpio y Mantenible**

### **Nombres descriptivos:**
```python
# ❌ Malo
def calc(x, y):
    return x * y * 0.1

# ✅ Bueno
def calcular_descuento_producto(precio_base, cantidad):
    PORCENTAJE_DESCUENTO = 0.1
    return precio_base * cantidad * PORCENTAJE_DESCUENTO
```

### **Funciones pequeñas y enfocadas:**
- Máximo 20-30 líneas por función
- Un nivel de abstracción por función
- Si necesitas comentarios para explicar bloques, probablemente necesitas una función separada

### **Evitar anidamiento profundo:**
```python
# ❌ Malo - demasiado anidamiento
def procesar_usuario(usuario):
    if usuario:
        if usuario.activo:
            if usuario.email:
                if validar_email(usuario.email):
                    enviar_bienvenida(usuario)

# ✅ Bueno - retorno temprano
def procesar_usuario(usuario):
    if not usuario:
        return
    if not usuario.activo:
        return
    if not usuario.email:
        return
    if not validar_email(usuario.email):
        return
    
    enviar_bienvenida(usuario)
```

## **Arquitectura Extensible y Resiliente**

### **Separación de responsabilidades por capas:**
```
📁 src/
├── 📁 presentation/     # Controllers, API endpoints
├── 📁 business/         # Lógica de negocio
├── 📁 data/            # Acceso a datos, repositorios
├── 📁 infrastructure/   # Servicios externos, configuración
└── 📁 shared/          # Utilidades comunes
```

### **Manejo de errores resiliente:**
- Usar excepciones específicas, no genéricas
- Implementar circuit breakers para servicios externos
- Logs detallados para debugging
- Timeouts apropiados en operaciones I/O

### **Configuración externa:**
- Usar variables de entorno para configuración
- Archivos de configuración por ambiente (dev, test, prod)
- No hardcodear valores en el código

### **Principios de diseño resiliente:**
- **Fail Fast**: Detectar errores temprano
- **Graceful Degradation**: El sistema sigue funcionando aunque algunos componentes fallen
- **Retry Logic**: Reintentos con backoff exponencial
- **Health Checks**: Monitoreo de salud de componentes

### **Extensibilidad:**
- Usar patrones como Strategy, Factory, Observer
- Interfaces bien definidas entre módulos
- Evitar acoplamiento fuerte entre componentes
- Documentar puntos de extensión claramente
