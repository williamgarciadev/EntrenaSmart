# Documentación Modular para Agentes de IA

Esta estructura permite mantener las instrucciones organizadas y fáciles de mantener.

## 📁 Estructura de archivos:

```
.github/
├── copilot-instructions.md      # Archivo principal con instrucciones esenciales
└── docs/                        # Documentación detallada modular
    ├── solid-principles.md      # Principios SOLID y código limpio
    ├── project-structure.md     # Organización de archivos y proyectos
    └── version-control.md       # Gestión de versiones con Git
```

## 🎯 Ventajas del enfoque modular:

- **Mantenibilidad**: Cada archivo se enfoca en un tema específico
- **Reutilización**: Los archivos se pueden copiar a otros proyectos independientemente
- **Claridad**: El archivo principal mantiene solo lo esencial
- **Escalabilidad**: Fácil agregar nuevos módulos sin sobrecargar el archivo principal

## 🚀 Uso recomendado:

1. **Para proyectos nuevos**: Copiar toda la carpeta `.github/` como template
2. **Para actualizaciones**: Modificar solo los archivos específicos necesarios
3. **Para proyectos específicos**: Agregar módulos adicionales según las necesidades del proyecto