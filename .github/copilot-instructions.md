# Instrucciones Generales para Agentes de IA

**IMPORTANTE: Responder siempre en español**

- Todas las respuestas y explicaciones deben ser en español
- Comentarios en el código en español
- Mensajes de commit en español
- Documentación y README en español
- Nombres de variables y funciones pueden ser en inglés (convención técnica)
- Logs y mensajes de error en español cuando sea posible
- Refactoriza el código siempre que mejore la claridad y mantenibilidad

## Behavior Rules

1. **No improvisar soluciones simplificadas.**  
   No generes proyectos, servidores, scripts ni ejemplos “mínimos funcionales” por tu cuenta.  
   Si detectas un error de dependencias o configuración, **describe el problema y su posible causa técnica**, pero **no crees un servidor o aplicación alternativa** para “hacerlo funcionar”.

2. **Responder con diagnóstico, no con reemplazo.**  
   Si el usuario te pide corregir un error, analiza y explica:  
   - Qué dependencias o versiones están causando conflicto.  
   - Cómo resolverlo en el contexto existente.  
   - Qué comando o archivo debe ajustarse.  
   Nunca reemplaces el stack, la arquitectura ni elimines partes del proyecto original.

3. **Mantener coherencia con el entorno del usuario.**  
   Siempre respeta el entorno tecnológico actual (por ejemplo: *FastAPI + Docker + Aurora Serverless en AWS*).  
   No propongas cambios radicales ni “simplificaciones” como eliminar Docker, usar SQLite o crear un servidor básico local.

4. **Ejemplo de respuesta correcta ante un error:**  
   > “El error indica un conflicto entre FastAPI y uvicorn en las versiones instaladas.  
   > Revisa el archivo `requirements.txt` y actualiza uvicorn a la versión compatible.  
   > No es necesario crear un nuevo servidor.”

5. **Ejemplo de respuesta prohibida:**  
   > “Veo que hay errores graves. Vamos a crear un servidor simple que funcione.”
   
## ✅ Instrucciones generales de trabajo

1. Primero, analiza el problema, revisa la base de código para identificar los archivos relevantes y escribe un plan en `tasks/todo.md`.

2. El plan debe contener una lista de tareas que puedas marcar como completadas conforme avances.

3. Antes de comenzar a trabajar, consulta conmigo para que pueda verificar y aprobar el plan.

4. Luego, comienza a ejecutar las tareas del plan, marcándolas como completadas a medida que las termines.

5. En cada paso, proporciona una explicación general y clara de los cambios que realizaste.

6. Haz cada tarea y cambio de código lo más simple posible. Evita cambios masivos. Cada cambio debe afectar la menor cantidad de código posible.

7. Finalmente, añade una sección de revisión al final del archivo con un resumen de los cambios que realizaste y cualquier información relevante adicional.

8. Realiza `commit` y `push` de los cambios después de cada tarea completada, siguiendo buenas prácticas en los mensajes de commit.

## 🔐 Revisión de seguridad

Antes de confirmar cada cambio:

- Asegurarse de que no haya datos sensibles expuestos en frontend o backend.
- Verificar que las API estén protegidas contra accesos indebidos.
- Revisar que los formularios tengan validación contra entradas maliciosas (XSS, SQLi).
- No dejar claves, tokens ni secretos en el código. Usar variables de entorno.

## 📘 Explicación de cambios

Después de cada tarea:

- Explica en lenguaje claro qué funcionalidad agregaste.
- Muestra qué archivos cambiaste y por qué.
- Enseña el flujo de cómo funciona, como si lo explicaras a un desarrollador junior.
- Usa ejemplos simples o comentarios clave si es útil.

## 🧠 Productividad creativa

Mientras se espera respuesta o carga:

- Usar el tiempo para pensar ideas nuevas (producto, contenido, negocios).
- Reflexionar sobre lo aprendido o lo que se puede mejorar del sistema.
- Aprovechar este chat como espacio creativo y estratégico.
- Puedes pedirme ayuda para lluvia de ideas, validación de conceptos o simplemente organizar tus pensamientos.

## 🎯 Buenas prácticas de desarrollo

### Convenciones de código:
- Usar nombres descriptivos en español para comentarios y documentación
- Seguir estándares del lenguaje (PEP 8 para Python, ESLint para JavaScript, etc.)
- Funciones pequeñas y con responsabilidad única
- Evitar código duplicado (DRY - Don't Repeat Yourself)

### Gestión de archivos:
- **MANTENER RAÍZ LIMPIA**: Solo archivos esenciales en el directorio raíz
- Crear directorio `tasks/` si no existe para documentar planes
- Mantener estructura limpia en `output/` para resultados
- Hacer backup de configuraciones importantes antes de modificar
- Organizar scripts por funcionalidad en subdirectorios apropiados

### Testing y validación:
- Probar cada funcionalidad después de implementarla
- Validar con datos reales cuando sea posible
- Documentar casos de prueba en español

## 📖 Documentación Modular

Para mantener estas instrucciones organizadas y manejables, la documentación detallada está dividida en módulos especializados:

### 🏗️ **[Principios SOLID y Código Limpio](docs/solid-principles.md)**
- Principios SOLID explicados con ejemplos
- Patrones de código limpio y mantenible
- Arquitectura extensible y resiliente
- Buenas prácticas de diseño de software

### � **[Buenas Prácticas Python](docs/python-best-practices.md)**
- Estándares de código y PEP 8
- Configuración de herramientas (Black, isort, pytest)
- Type hints y documentación
- Testing, logging y manejo de errores
- Optimizaciones de rendimiento y seguridad

### �📁 **[Estructura de Proyecto](docs/project-structure.md)**
- Organización de archivos y directorios
- Reglas para mantener la raíz limpia
- Estructura recomendada por tipo de proyecto
- Estrategias de limpieza automática

### 🔄 **[Gestión de Versiones](docs/version-control.md)**
- Flujo de trabajo con Git y ramas
- Convenciones de nombres y mensajes de commit
- Proceso de releases y versionado
- Comandos Git esenciales

## 📋 Estructura de planificación

### Formato para `tasks/todo.md`:
```markdown
# Plan de Trabajo: [Título del proyecto]

## 📝 Resumen
Descripción breve de lo que se va a implementar.

## 🎯 Objetivos
- [ ] Objetivo 1
- [ ] Objetivo 2

## 📋 Tareas
### Fase 1: Preparación
- [ ] Tarea 1
- [ ] Tarea 2

### Fase 2: Implementación
- [ ] Tarea 3
- [ ] Tarea 4

## ✅ Revisión Final
(Se completa al finalizar)
- Resumen de cambios realizados
- Archivos modificados
- Funcionalidades agregadas
- Notas importantes
```