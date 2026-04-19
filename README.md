# Sistema de Gestión de Inventario
  
**Dominio:** Dominio 3 — Sistema de Gestión de Inventario  
**Fecha:** Abril 2026

---

## ¿Qué problema resuelve?

Este sistema permite llevar un control completo del inventario de productos de TechNova Solutions. Registra entradas y salidas de stock, monitorea los niveles en tiempo real y genera alertas automáticas cuando un producto cae por debajo del nivel mínimo definido, evitando desabasto.

---

## Estructura de la Base de Datos

| Tabla | Descripción | Relación |
|-------|-------------|----------|
| `categorias` | Agrupa los productos por tipo | Tabla raíz |
| `productos` | Nombre, precio, cantidad y stock mínimo | Pertenece a `categorias` |
| `movimientos` | Historial de entradas y salidas | Pertenece a `productos` |
| `alertas_reposicion` | Alertas generadas cuando el stock queda bajo | Pertenece a `productos` |

---

## Rutas de la API

| Método | Ruta | Qué hace |
|--------|------|----------|
| GET | `/` | Interfaz HTML principal |
| POST | `/productos` | Registra un nuevo producto |
| GET | `/productos` | Consulta el stock actual de todos los productos |
| POST | `/movimientos` | Registra una entrada o salida de inventario |
| GET | `/productos/bajo-stock` | Lista productos por debajo del stock mínimo |
| GET | `/alertas` | Muestra todas las alertas de reposición |
| GET | `/categorias` | Lista las categorías disponibles |

---

## ¿Cuál es la tarea pesada y por qué bloquea el sistema?

La tarea pesada ocurre en la ruta `POST /movimientos`. Cuando se registra una salida y el stock resultante queda igual o por debajo del mínimo, el sistema ejecuta un `time.sleep(6)` que simula un proceso costoso como el envío de notificaciones al proveedor o la generación de una orden de compra. El problema es que Flask en modo por defecto corre en un solo hilo, por lo que si dos usuarios hacen una salida al mismo tiempo y ambas disparan la alerta, el segundo tiene que esperar a que el primero termine sus 6 segundos, bloqueando el servidor completo durante ese tiempo.

---

## Cómo levantar el proyecto

```bash
# 1. Clonar el repositorio
git clone al repositorio
cd inventario

# 2. Crear las tablas en RDS
mysql -h ENDPOINT_RDS -u admin -p < schema.sql

# 3. Construir la imagen Docker
docker build -t inventario-app .

# 4. Correr el contenedor
docker run -d -p 3000:3000 \
  -e DB_HOST=ENDPOINT_RDS \
  -e DB_USER=admin \
  -e DB_PASSWORD=contraseña \
  -e DB_NAME=inventario_db \
  inventario-app

# 5. Abrir en navegador
http://IP_EC2:3000
```

---

## Decisiones técnicas

Diseñe cuatro tablas porque separar categorias de productos hace el sistema más flexible y normalizado. Los movimientos se guardan en su propia tabla para mantener un historial completo y auditable. Las alertas también se persisten en la base de datos en lugar de solo imprimirse, lo que permite consultarlas desde la interfaz. Todo el manejo de errores sigue el patrón try/except/finally para garantizar que las conexiones siempre se cierren. Las credenciales nunca están en el código, se pasan exclusivamente por variables de entorno al correr el contenedor.
