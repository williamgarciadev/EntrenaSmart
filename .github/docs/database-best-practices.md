# 📋 Guía de Buenas Prácticas: Diseño de Bases de Datos con GeneXus

## 🎯 Propósito y Alcance

Este documento define **buenas prácticas y estándares obligatorios** para **generar código SQL, diseñar modelos de datos o crear scripts DDL/DML** en proyectos GeneXus.[1][2]

**Objetivos principales:**
- Garantizar modelos normalizados hasta **Tercera Forma Normal (3FN)** mínimo[3][4]
- Aplicar **nomenclatura GIK (GeneXus Incremental Knowledge Base)** de forma consistente[5][1]
- Promover uso estratégico de **dominios** para propagación de cambios[6][7]
- Asegurar **integridad referencial y escalabilidad**[4][8]

---

## 🧭 Principios Fundamentales

### Nomenclatura GIK de GeneXus

La **nomenclatura GIK** es el estándar oficial de GeneXus para nombrar atributos y asegurar consistencia en la base de conocimiento.[1][5]

**Estructura de nombre de atributo:**
```
Nombre del Objeto/Transacción [+ Nivel] + Categoría [+ Calificador] [+ Complemento]
```

**Componentes:**

| Componente | Descripción | Obligatorio | Ejemplo |
|------------|-------------|-------------|---------|
| **Objeto/Transacción** | Nombre de la entidad (Transaction object name) | ✅ Sí | `Cliente`, `Factura`, `FacturaLinea` |
| **Nivel** | Nombre del nivel secundario si aplica | ❌ No | `FacturaLinea` (línea dentro de `Factura`) |
| **Categoría** | Rol semántico del atributo (máx 10 caracteres) | ✅ Sí | `Id`, `Codigo`, `Nombre`, `Fecha`, `Descripcion`, `Precio`, `Monto` |
| **Calificador** | Especifica el contexto de la categoría | ❌ No | `Registro` en `ClienteFechaRegistro`, `Nacimiento` en `ClienteFechaNacimiento` |
| **Complemento** | Información adicional específica | ❌ No | `Postal` en `ClienteCodigoPostal` |

**Ejemplos correctos aplicando GIK:**

```
✅ ClienteId                   // Cliente + Id (identificador)
✅ ClienteNombre               // Cliente + Nombre
✅ ClienteFechaRegistro        // Cliente + Fecha + Calificador (Registro)
✅ PaisId                      // Pais + Id
✅ PaisNombre                  // Pais + Nombre
✅ PaisCiudadId               // Pais + Ciudad (nivel) + Id
✅ PaisCiudadNombre           // Pais + Ciudad (nivel) + Nombre
✅ FacturaId                   // Factura + Id
✅ FacturaFecha                // Factura + Fecha
✅ FacturaLineaId             // Factura + Linea (nivel) + Id
✅ FacturaLineaCantidad       // Factura + Linea (nivel) + Cantidad
✅ ProductoPrecioVenta        // Producto + Precio + Calificador (Venta)
✅ AtraccionDireccion         // Atraccion + Direccion
✅ ClienteDireccionPostal     // Cliente + Direccion + Complemento (Postal)
```

**Ejemplos incorrectos:**

```
❌ Cli_Cod                     // Abreviatura + prefijo innecesario
❌ tblCliente                  // Prefijo de tabla
❌ client_id                   // snake_case (no es convención GeneXus)
❌ IdCliente                   // Categoría antes del objeto
❌ Codigo                      // Falta nombre de objeto
❌ DescripcionProducto         // Categoría antes del objeto
```

### Beneficios de la Nomenclatura GIK

La nomenclatura GIK ofrece ventajas críticas en desarrollo GeneXus:[2][1]

1. **Normalización automática:** GeneXus detecta relaciones por nombres coincidentes (`ClienteId` en múltiples tablas)
2. **Refactorización segura:** Cambiar un atributo propaga cambios a todos los objetos que lo usan
3. **Código autodocumentado:** `FacturaClienteFechaEmision` es inmediatamente comprensible
4. **Navegación inteligente:** El IDE sugiere atributos relacionados por prefijo
5. **Compatibilidad con patterns:** Los patterns de GeneXus esperan esta nomenclatura[2]

### Dominios en GeneXus

Los **dominios** definen tipos de datos reutilizables que agrupan atributos y variables con características comunes.[7][9][6]

**¿Cuándo usar dominios?**

- Atributos/variables con **la misma definición** (tipo, longitud, formato)[6]
- Propiedades compartidas: `Autonumber`, `Picture`, `Input/Output`[7]
- Validaciones comunes: rangos, formatos, reglas de negocio[9]

**Ejemplos de dominios:**

```
Dominio: Id
  Tipo: Numeric(6,0)
  Autonumber: True
  Propiedades: Identificador numérico autoincremental
  Usado en: ClienteId, ProductoId, FacturaId, PaisId

Dominio: Name
  Tipo: VarChar(100)
  Picture: @!
  Propiedades: Nombres en mayúsculas iniciales
  Usado en: ClienteNombre, ProductoNombre, PaisNombre

Dominio: Description
  Tipo: VarChar(255)
  Propiedades: Descripciones textuales extensas
  Usado en: ProductoDescripcion, CategoriaDescripcion

Dominio: Money
  Tipo: Decimal(18,2)
  Picture: Z,ZZZ,ZZ9.99
  Propiedades: Valores monetarios con 2 decimales
  Usado en: ProductoPrecio, FacturaMonto, ClienteSaldo

Dominio: Date
  Tipo: Date
  Picture: 99/99/9999
  Propiedades: Fechas sin hora
  Usado en: FacturaFecha, ClienteFechaRegistro

Dominio: Email
  Tipo: VarChar(100)
  Validación: Formato email válido
  Usado en: ClienteEmail, ProveedorEmail
```

**Ventajas de dominios bien definidos:**[9][6][7]

1. **Propagación de cambios:** Modificar `Money` de `DECIMAL(18,2)` a `DECIMAL(20,4)` actualiza todos los atributos monetarios
2. **Consistencia visual:** Todos los `Money` muestran formato `$1,234.56`
3. **Validación centralizada:** Regla en dominio `Email` valida en toda la aplicación
4. **Detección de errores:** Asignar `PesoKG` a `PesoToneladas` genera advertencia[9]
5. **Agrupación lógica:** Filtrar "todos los atributos tipo `Money`" para auditorías

**Antipatrón - No usar dominios:**

```sql
-- ❌ Sin dominios: definiciones redundantes e inconsistentes
CREATE TABLE Cliente (
    ClienteId INT IDENTITY(1,1),          -- Manual
    ClienteNombre VARCHAR(50),            -- 50 caracteres
    ClienteEmail VARCHAR(100)             -- Sin validación
);

CREATE TABLE Producto (
    ProductoId INT,                       -- Sin autonumber
    ProductoNombre VARCHAR(100),          -- 100 caracteres (inconsistente)
    ProductoPrecio DECIMAL(10,2)          -- Precisión diferente
);

-- ✅ Con dominios: consistencia automática
-- Dominio Id: Numeric(6,0), Autonumber=True
-- Dominio Name: VarChar(100)
-- Dominio Money: Decimal(18,2)

CREATE TABLE Cliente (
    ClienteId INT IDENTITY(1,1),          -- Basado en dominio Id
    ClienteNombre VARCHAR(100),           -- Basado en dominio Name
    ClienteEmail VARCHAR(100)             -- Basado en dominio Email
);

CREATE TABLE Producto (
    ProductoId INT IDENTITY(1,1),         -- Basado en dominio Id
    ProductoNombre VARCHAR(100),          -- Basado en dominio Name
    ProductoPrecio DECIMAL(18,2)          -- Basado en dominio Money
);
```

### Normalización de Datos

**Cumplir hasta Tercera Forma Normal (3FN)** es obligatorio:[3][4]

- **1FN:** Eliminar valores repetidos, asegurar atomicidad por columna
- **2FN:** Remover dependencias parciales en claves compuestas
- **3FN:** Eliminar dependencias transitivas entre columnas no clave
- **Justificación obligatoria:** Cualquier desnormalización requiere documentación de métricas de rendimiento

**Ejemplo de normalización:**

```sql
-- ❌ Violación de 3FN: Ciudad depende transitivamente de ClienteId a través de PaisId
CREATE TABLE Cliente (
    ClienteId INT PRIMARY KEY,
    ClienteNombre VARCHAR(100),
    PaisId INT,
    PaisNombre VARCHAR(100),          -- Redundante
    CiudadId INT,
    CiudadNombre VARCHAR(100)         -- Redundante
);

-- ✅ Normalizado a 3FN con nomenclatura GIK
CREATE TABLE Pais (
    PaisId INT PRIMARY KEY,
    PaisNombre VARCHAR(100) NOT NULL
);

CREATE TABLE Ciudad (
    CiudadId INT PRIMARY KEY,
    PaisId INT NOT NULL,
    CiudadNombre VARCHAR(100) NOT NULL,
    CONSTRAINT FK_Pais_Ciudad FOREIGN KEY (PaisId) 
        REFERENCES Pais(PaisId)
);

CREATE TABLE Cliente (
    ClienteId INT PRIMARY KEY,
    ClienteNombre VARCHAR(100) NOT NULL,
    CiudadId INT NOT NULL,
    CONSTRAINT FK_Ciudad_Cliente FOREIGN KEY (CiudadId) 
        REFERENCES Ciudad(CiudadId)
);
```

### Integridad Referencial

**Todas las relaciones deben ser explícitas:**[10][4]

- Definir `PRIMARY KEY` en cada tabla
- Declarar `FOREIGN KEY` para todas las relaciones
- Aplicar restricciones `ON DELETE` y `ON UPDATE` según reglas de negocio
- Nombrar constraints con formato estándar

**Nomenclatura de constraints:**

```sql
PK_<NombreTabla>                          -- Clave primaria
FK_<TablaPadre>_<TablaHija>               -- Clave foránea
CHK_<NombreTabla>_<Atributo>              -- Validación CHECK
UQ_<NombreTabla>_<Atributo>               -- Restricción UNIQUE
IX_<NombreTabla>_<Atributo>               -- Índice
DF_<NombreTabla>_<Atributo>               -- Valor DEFAULT
```

**Ejemplo completo:**

```sql
CREATE TABLE Cliente (
    ClienteId INT IDENTITY(1,1),
    ClienteNombre VARCHAR(100) NOT NULL,
    ClienteEmail VARCHAR(100),
    ClienteFechaRegistro DATE DEFAULT GETDATE(),
    ClienteActivo BIT DEFAULT 1,
    CONSTRAINT PK_Cliente PRIMARY KEY (ClienteId),
    CONSTRAINT UQ_Cliente_Email UNIQUE (ClienteEmail),
    CONSTRAINT CHK_Cliente_Email CHECK (ClienteEmail LIKE '%_@_%._%')
);

CREATE TABLE Pedido (
    PedidoId INT IDENTITY(1,1),
    ClienteId INT NOT NULL,
    PedidoFecha DATETIME2(7) DEFAULT SYSDATETIME(),
    PedidoMonto DECIMAL(18,2) NOT NULL,
    CONSTRAINT PK_Pedido PRIMARY KEY (PedidoId),
    CONSTRAINT FK_Cliente_Pedido FOREIGN KEY (ClienteId) 
        REFERENCES Cliente(ClienteId) ON DELETE CASCADE,
    CONSTRAINT CHK_Pedido_Monto CHECK (PedidoMonto > 0)
);

CREATE INDEX IX_Pedido_ClienteId ON Pedido(ClienteId);
CREATE INDEX IX_Pedido_Fecha ON Pedido(PedidoFecha);
```

### Tipos de Datos según Dominios

Mapeo de dominios GeneXus a SQL Server:[10][6]

| Dominio GeneXus | Tipo SQL Server | Uso Recomendado | Ejemplo Atributo |
|-----------------|-----------------|-----------------|------------------|
| `Id` | `INT IDENTITY(1,1)` | Claves primarias autonuméricas | `ClienteId`, `ProductoId` |
| `Code` | `VARCHAR(20)` | Códigos alfanuméricos | `ClienteCodigo`, `ProductoCodigo` |
| `Name` | `VARCHAR(100)` | Nombres cortos | `ClienteNombre`, `PaisNombre` |
| `Description` | `VARCHAR(255)` | Descripciones textuales | `ProductoDescripcion` |
| `Money` | `DECIMAL(18,2)` | Valores monetarios | `ProductoPrecio`, `FacturaMonto` |
| `Percent` | `DECIMAL(5,2)` | Porcentajes | `ProductoDescuento` |
| `Date` | `DATE` | Fechas sin hora | `ClienteFechaRegistro` |
| `DateTime` | `DATETIME2(7)` | Fechas con hora precisa | `PedidoFechaHora` |
| `Boolean` | `BIT` | Flags true/false | `ClienteActivo`, `ProductoVisible` |
| `Email` | `VARCHAR(100)` | Correos electrónicos | `ClienteEmail` |
| `Phone` | `VARCHAR(20)` | Números telefónicos | `ClienteTelefono` |
| `URL` | `VARCHAR(255)` | URLs/enlaces | `ProductoImagenURL` |
| `Address` | `VARCHAR(200)` | Direcciones físicas | `ClienteDireccion` |
| `Geolocation` | `GEOGRAPHY` | Coordenadas GPS | `SucursalUbicacion` |
| `LongText` | `VARCHAR(MAX)` | Textos extensos | `ArticuloContenido` |
| `Image` | `VARBINARY(MAX)` | Imágenes binarias | `ProductoImagen` |

**Restricciones por tipo de dominio:**

```sql
-- Dominio Money: siempre positivo, 2 decimales
ALTER TABLE Producto
ADD CONSTRAINT CHK_Producto_Precio 
CHECK (ProductoPrecio > 0 AND ProductoPrecio <= 9999999.99);

-- Dominio Percent: rango 0-100
ALTER TABLE Promocion
ADD CONSTRAINT CHK_Promocion_Descuento 
CHECK (PromocionDescuento BETWEEN 0 AND 100);

-- Dominio Email: formato válido
ALTER TABLE Cliente
ADD CONSTRAINT CHK_Cliente_Email 
CHECK (ClienteEmail LIKE '%_@_%._%');

-- Dominio Date: no fechas futuras para registro
ALTER TABLE Cliente
ADD CONSTRAINT CHK_Cliente_FechaRegistro 
CHECK (ClienteFechaRegistro <= GETDATE());
```

***

## 🏗️ Patrones de Diseño en GeneXus

### Transacciones con Niveles

GeneXus soporta **estructuras jerárquicas** (transacciones con niveles) que se traducen a relaciones 1:N.[11][2]

**Ejemplo: Factura con FacturaLinea**

```sql
-- Nivel principal: Factura
CREATE TABLE Factura (
    FacturaId INT IDENTITY(1,1) PRIMARY KEY,
    ClienteId INT NOT NULL,
    FacturaFecha DATE DEFAULT GETDATE(),
    FacturaMonto DECIMAL(18,2),
    CONSTRAINT FK_Cliente_Factura FOREIGN KEY (ClienteId) 
        REFERENCES Cliente(ClienteId)
);

-- Nivel secundario: FacturaLinea (nomenclatura GIK completa)
CREATE TABLE FacturaLinea (
    FacturaLineaId INT IDENTITY(1,1) PRIMARY KEY,
    FacturaId INT NOT NULL,                    -- FK al nivel padre
    ProductoId INT NOT NULL,
    FacturaLineaCantidad INT NOT NULL,
    FacturaLineaPrecioUnitario DECIMAL(18,2),
    FacturaLineaSubtotal DECIMAL(18,2),
    CONSTRAINT FK_Factura_FacturaLinea FOREIGN KEY (FacturaId) 
        REFERENCES Factura(FacturaId) ON DELETE CASCADE,
    CONSTRAINT FK_Producto_FacturaLinea FOREIGN KEY (ProductoId) 
        REFERENCES Producto(ProductoId),
    CONSTRAINT CHK_FacturaLinea_Cantidad 
        CHECK (FacturaLineaCantidad > 0)
);
```

**Nomenclatura en niveles:**
- Nivel padre: `Factura` → Atributos: `FacturaId`, `FacturaFecha`, `FacturaMonto`
- Nivel hijo: `FacturaLinea` → Atributos: `FacturaLineaId`, `FacturaLineaCantidad`, `FacturaLineaPrecioUnitario`

### Relaciones N:M con Tabla Intermedia

Resolver relaciones muchos-a-muchos con entidad asociativa:[4][3]

```sql
CREATE TABLE Producto (
    ProductoId INT IDENTITY(1,1) PRIMARY KEY,
    ProductoNombre VARCHAR(100) NOT NULL,
    ProductoPrecio DECIMAL(18,2)
);

CREATE TABLE Categoria (
    CategoriaId INT IDENTITY(1,1) PRIMARY KEY,
    CategoriaNombre VARCHAR(100) NOT NULL,
    CategoriaDescripcion VARCHAR(255)
);

-- Tabla intermedia (sin transacción GeneXus directa)
CREATE TABLE ProductoCategoria (
    ProductoId INT NOT NULL,
    CategoriaId INT NOT NULL,
    ProductoCategoriaFechaAsignacion DATE DEFAULT GETDATE(),
    CONSTRAINT PK_ProductoCategoria PRIMARY KEY (ProductoId, CategoriaId),
    CONSTRAINT FK_Producto_ProductoCategoria FOREIGN KEY (ProductoId) 
        REFERENCES Producto(ProductoId) ON DELETE CASCADE,
    CONSTRAINT FK_Categoria_ProductoCategoria FOREIGN KEY (CategoriaId) 
        REFERENCES Categoria(CategoriaId) ON DELETE CASCADE
);
```

### Subtipos (SDT - Subtypes)

GeneXus maneja subtipos mediante **grupos de subtipos** con nomenclatura específica:[2]

```sql
-- Supertipo: Banco
CREATE TABLE Banco (
    BancoId INT PRIMARY KEY,
    BancoNombre VARCHAR(100) NOT NULL
);

-- Grupo de subtipos: BancoOrigen
CREATE TABLE TransaccionBancaria (
    TransaccionId INT PRIMARY KEY,
    BancoIdOrigen INT NOT NULL,              -- Subtipo del grupo "Origen"
    BancoNombreOrigen VARCHAR(100),          -- Atributo inferido
    BancoIdDestino INT NOT NULL,             -- Subtipo del grupo "Destino"
    BancoNombreDestino VARCHAR(100),         -- Atributo inferido
    TransaccionMonto DECIMAL(18,2),
    CONSTRAINT FK_BancoOrigen FOREIGN KEY (BancoIdOrigen) 
        REFERENCES Banco(BancoId),
    CONSTRAINT FK_BancoDestino FOREIGN KEY (BancoIdDestino) 
        REFERENCES Banco(BancoId)
);
```

**Nomenclatura de subtipos:**
- Grupo primario: `BancoIdOrigen` (en lugar de solo `BancoId`)
- Atributo concatenado: `BancoNombreOrigen` (inferido desde `BancoNombre`)

### Atributos Fórmula (Formula Attributes)

Cuando un atributo se define mediante **UDP (User Defined Procedure)**:[2]

```
ClienteSaldoResidual = udp(PClienteSaldoResidual, ClienteId)
```

**Nomenclatura del procedimiento:**
- Opción 1: Mismo nombre del atributo → `PClienteSaldoResidual`
- Opción 2: Partícula "Frm" → `PFrmClienteSaldoResidual`

### Campos de Auditoría

Incluir campos estándar en tablas transaccionales:[8][2]

```sql
CREATE TABLE Pedido (
    PedidoId INT IDENTITY(1,1) PRIMARY KEY,
    ClienteId INT NOT NULL,
    PedidoFecha DATE DEFAULT GETDATE(),
    PedidoMonto DECIMAL(18,2),
    -- Campos de auditoría con nomenclatura GIK
    PedidoFechaCreacion DATETIME2(7) DEFAULT SYSDATETIME() NOT NULL,
    PedidoUsuarioCreacion VARCHAR(100) DEFAULT SYSTEM_USER NOT NULL,
    PedidoFechaModificacion DATETIME2(7),
    PedidoUsuarioModificacion VARCHAR(100),
    PedidoActivo BIT DEFAULT 1 NOT NULL,
    CONSTRAINT FK_Cliente_Pedido FOREIGN KEY (ClienteId) 
        REFERENCES Cliente(ClienteId)
);
```

***

## ⚠️ Antipatrones a Evitar

### Violaciones de Nomenclatura GIK

| Antipatrón | Problema | Solución GIK |
|------------|----------|--------------|
| `IdCliente` | Categoría antes del objeto | `ClienteId` |
| `Cli_Cod` | Abreviatura + prefijo | `ClienteCodigo` |
| `client_name` | snake_case no es convención GeneXus | `ClienteNombre` |
| `FechaFactura` | Categoría antes del objeto | `FacturaFecha` |
| `tblProductos` | Prefijo de tabla + plural | `Producto` (singular) |
| `Descripcion` | Falta nombre de objeto | `ProductoDescripcion` |
| `EmailContacto` | Categoría ambigua | `ClienteEmail` o `ContactoEmail` |

### Violaciones de Normalización

| Antipatrón | Problema | Solución |
|------------|----------|----------|
| Columnas repetitivas (`ClienteDireccion1`, `ClienteDireccion2`) | Viola 1FN, limita escalabilidad | Tabla `ClienteDireccion` con 1:N |
| Valores CSV (`ProductoEtiquetas: 'nuevo,oferta,destacado'`) | No permite búsquedas eficientes | Tabla intermedia `ProductoEtiqueta` |
| Redundancia calculada sin justificar (`FacturaTotalConImpuesto`) | Riesgo de inconsistencia | Columna calculada persistida o formula attribute |
| Mezcla de conceptos (`PersonaClienteProveedor`) | Confunde responsabilidades | Separar `Cliente` y `Proveedor` con FK a `Persona` |

### Errores de Dominios

**Nunca hacer:**[6][7][9]

- Atributos sin dominio definido (pérdida de propagación de cambios)
- Dominios diferentes para mismo concepto (`Money` vs `Currency` vs `Amount`)
- Operaciones entre dominios incompatibles (`PesoKG = PesoToneladas + Carga` sin conversión)
- Redefinir tipo en atributo cuando debería cambiar el dominio

**Ejemplo de inconsistencia:**

```sql
-- ❌ Sin dominios: mezcla de definiciones
CREATE TABLE Producto (
    ProductoId INT,                    -- Sin autonumber
    ProductoPrecio DECIMAL(10,2)       -- 10 dígitos
);

CREATE TABLE Servicio (
    ServicioId INT IDENTITY(1,1),      -- Con autonumber (inconsistente)
    ServicioPrecio DECIMAL(18,2)       -- 18 dígitos (inconsistente)
);

-- ✅ Con dominios: garantiza consistencia
-- Dominio Id: Numeric(6,0), Autonumber=True
-- Dominio Money: Decimal(18,2)
CREATE TABLE Producto (
    ProductoId INT IDENTITY(1,1),      -- Basado en dominio Id
    ProductoPrecio DECIMAL(18,2)       -- Basado en dominio Money
);

CREATE TABLE Servicio (
    ServicioId INT IDENTITY(1,1),      -- Basado en dominio Id
    ServicioPrecio DECIMAL(18,2)       -- Basado en dominio Money
);
```

***

## 🧠 Comportamiento del Asistente IA

Cuando detecte problemas de diseño, el asistente debe:

1. **Identificar violación específica:** "Viola nomenclatura GIK: la categoría `Id` debe ir después del objeto" o "Viola 3FN: `PaisNombre` depende transitivamente de `ClienteId`"[1][3]
2. **Explicar impacto técnico:** "Sin nomenclatura GIK, GeneXus no detectará automáticamente la relación entre `Cliente` y `Pedido`"
3. **Proponer corrección completa:** Incluir DDL con nomenclatura GIK, dominios y constraints
4. **Sugerir dominios apropiados:** "Estos atributos deberían basarse en el dominio `Money`"[6]
5. **Solicitar contexto si falta información:** "¿`FacturaLinea` es un nivel dentro de `Factura`?"

### Ejemplo de Análisis Correcto

**Usuario:** "Crea una tabla Producto con IdProducto, NombreProducto, Precio"

**Respuesta del Asistente:**

```
❌ Detectadas 3 violaciones:
1. Nomenclatura GIK incorrecta: "IdProducto" → debe ser "ProductoId"
2. Nomenclatura GIK incorrecta: "NombreProducto" → debe ser "ProductoNombre"
3. Falta definición de dominios para propagación de cambios

✅ Propuesta corregida con nomenclatura GIK y dominios:

-- Primero, definir dominios (si no existen):
-- Dominio Id: Numeric(6,0), Autonumber=True
-- Dominio Name: VarChar(100)
-- Dominio Money: Decimal(18,2)

CREATE TABLE Producto (
    ProductoId INT IDENTITY(1,1),          -- Basado en dominio Id
    ProductoNombre VARCHAR(100) NOT NULL,  -- Basado en dominio Name
    ProductoPrecio DECIMAL(18,2) NOT NULL, -- Basado en dominio Money
    ProductoDescripcion VARCHAR(255),      -- Basado en dominio Description
    ProductoActivo BIT DEFAULT 1,          -- Basado en dominio Boolean
    CONSTRAINT PK_Producto PRIMARY KEY (ProductoId),
    CONSTRAINT CHK_Producto_Precio CHECK (ProductoPrecio > 0)
);

-- Agregar índices para búsquedas frecuentes
CREATE INDEX IX_Producto_Nombre ON Producto(ProductoNombre);

-- Documentar tabla
EXEC sys.sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Catálogo de productos comercializables', 
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'Producto';

Justificación:
- Nomenclatura GIK: Facilita navegación en KB de GeneXus
- Dominios: Cambiar precisión de Money afecta todos los precios simultáneamente
- Constraints: Valida integridad antes de llegar a lógica de negocio
```

***

## 🎯 Reglas de Compromiso

### Priorizar Convenciones GeneXus

- **Siempre aplicar nomenclatura GIK** salvo justificación explícita[5][1]
- **Usar dominios para todo atributo/variable** que comparta definición[7][6]
- **Respetar estructura de niveles** en transacciones jerárquicas[11]
- **Seguir patrones GeneXus** para Web/Mobile (Work With, Patterns)[2]

### Documentar Decisiones

Cada propuesta debe incluir justificación técnica:[10][2]

- "Se usa dominio `Money` para facilitar cambio global de precisión decimal"
- "Nomenclatura GIK `ClienteFechaRegistro` permite a GeneXus inferir relación con `Cliente`"
- "Se normaliza a 3FN para eliminar redundancia entre `Ciudad` y `Pais`"
- "Se crea nivel `FacturaLinea` porque GeneXus maneja automáticamente CASCADE en niveles"

### Propagar Cambios desde Dominios

Explicar cómo dominios facilitan mantenimiento:[7][9][6]

```
Al usar dominio Money (DECIMAL 18,2):
- Todos los atributos ProductoPrecio, FacturaMonto, ClienteSaldo 
  se actualizan simultáneamente
- Cambio en Picture afecta a toda la aplicación
- Validaciones CHECK se propagan automáticamente
```

### Respetar Limitaciones de GeneXus

- **No usar triggers complejos:** GeneXus genera triggers automáticamente, evitar conflictos[12]
- **No renombrar tablas generadas:** GeneXus mapea transacciones a tablas por convención
- **Índices en FK:** GeneXus los crea automáticamente, documentar adicionales[12]
- **CASCADE en niveles:** Automático en niveles de transacciones, manual en otras relaciones

***

## 📐 Checklist de Validación

Antes de finalizar un diseño, verificar:

**Nomenclatura:**
- [ ] Todos los atributos siguen nomenclatura GIK: `Objeto + [Nivel] + Categoría + [Calificador]`[5][1]
- [ ] Tablas en singular PascalCase: `Cliente`, `FacturaLinea`[2]
- [ ] Sin prefijos innecesarios: no `tbl_`, `fld_`, `col_`[2]
- [ ] Constraints nombrados: `PK_`, `FK_`, `CHK_`, `UQ_`, `IX_`

**Dominios:**
- [ ] Atributos similares basados en mismo dominio (`Id`, `Name`, `Money`)[6][7]
- [ ] Propiedades heredadas desde dominios (`Autonumber`, `Picture`)[7]
- [ ] Variables también basadas en dominios para validación estricta[9]

**Normalización:**
- [ ] Cumple 3FN sin redundancia injustificada[3][4]
- [ ] Todas las tablas tienen `PRIMARY KEY`[10]
- [ ] Todas las relaciones tienen `FOREIGN KEY` explícita[4]
- [ ] Tipos de datos apropiados (`DECIMAL` para dinero, `DATETIME2` para fechas)[13]

**Integridad:**
- [ ] Restricciones `NOT NULL` en campos obligatorios
- [ ] Restricciones `CHECK` para validaciones de dominio
- [ ] Índices en FK y columnas de búsqueda frecuente[8]
- [ ] Campos de auditoría en tablas transaccionales críticas

**Documentación:**
- [ ] Comentarios SQL en lógica compleja
- [ ] Extended properties describiendo tablas
- [ ] Justificación de desnormalizaciones (si existen)

---

## 📚 Referencias y Estándares

### Documentación GeneXus Oficial

- **GIK Naming Convention** - Nomenclatura estándar de atributos[1][5]
- **Attribute Definition** - Definición de atributos y propiedades[12]
- **Attributes and Domains** - Uso estratégico de dominios[6][7]
- **Best Practices of Programming in GeneXus** - Buenas prácticas generales[2]
- **Database Reverse Engineering Tool (DBRET)** - Ingeniería inversa de BD[12]

### Referencias Académicas

- Codd, E. F. (1970) - *A Relational Model of Data for Large Shared Data Banks*
- Date, C. J. - *An Introduction to Database Systems* (8th Edition)
- Hernández, M. J. - *Database Design for Mere Mortals* (3rd Edition)

### Estándares de Industria

- ISO/IEC 9075:2023 - SQL Standard
- Microsoft SQL Server Design Guide (MSDN)[14]
- ANSI X3.135 - Database Language SQL

### Recursos Complementarios

- **Normalización de Bases de Datos** - 1FN, 2FN, 3FN, BCNF[3][4]
- **Database Management Best Practices 2025** - Prácticas modernas[8]
- **Atributos basados en dominios y variables** - Validaciones estrictas[9]

***

## 🔄 Mantenimiento del Documento

**Última actualización:** Noviembre 2025  
**Versión:** 3.0  
**Cambios principales:** Integración completa de nomenclatura GIK y dominios GeneXus  
**Próxima revisión:** Trimestral o con cambios mayores en GeneXus/SQL Server

Este documento debe evolucionar con nuevas versiones de GeneXus, SQL Server y aprendizajes del equipo de desarrollo.

***

[1](https://docs.genexus.com/en/wiki?9020%2CGIK+Naming+Convention)
[2](https://docs.genexus.com/en/wiki?27328%2CBest+Practices+of+Programming+in+GeneXus)
[3](https://www.digitalocean.com/community/tutorials/database-normalization)
[4](https://dev.to/nilebits/understanding-database-normalization-48n6)
[5](https://docs.genexus.com/en/wiki?1872%2CNomenclatura+GIK+%28Spanish%29)
[6](https://training.genexus.com/en/learning/pdf/attributes-and-domains-pdf-6104678)
[7](https://training.genexus.com/es/aprendiendo/pdf/atributos-y-dominios-pdf-6104678)
[8](https://www.instaclustr.com/education/data-architecture/8-database-management-best-practices-to-know-in-2025/)
[9](https://ealmeida.blogspot.com/2018/08/atributos-basados-en-dominios-y_15.html)
[10](https://www.c-sharpcorner.com/article/best-practices-for-effective-database-design-in-sql-server/)
[11](https://training.genexus.com/en/learning/pdf/attribute-nomenclature-pdf)
[12](https://www.genexus.com/en/news/read-news/using-the-genexus-database-reverse-engineering-tool)
[13](https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17)
[14](https://learn.microsoft.com/en-us/system-center/scom/plan-sqlserver-design?view=sc-om-2025)
[15](https://docs.genexus.com/en/wiki)
[16](https://docs.genexus.com/en/wiki?2823%2CGIK+%26+GxSoft+Nomenclatures)
[17](https://training.genexus.com/en/learning/video/creation-of-a-transaction)
[18](https://docs.genexus.com/en/wiki?52444%2CDomains+for+Dynamics+Forms+%28GeneXus+17+or+prior%29%2C)
[19](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/971575/76f9315a-86f8-4dc4-8bc9-35e2591457de/database-best-practices1.md)