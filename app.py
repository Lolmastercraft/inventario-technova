# Sistema de Gestion de Inventario - Dominio 3
# TechNova Solutions
# Flask + MySQL (AWS RDS)

import os
import time
import mysql.connector
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Conexion a la base de datos usando variables de entorno
def get_db_connection():
    connection = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "admin"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "inventario_db"),
        port=int(os.environ.get("DB_PORT", 3306))
    )
    return connection


# Plantilla HTML de la interfaz principal
HTML_PRINCIPAL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Inventario - TechNova</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; color: #333; }
        header {
            background: #1a1a2e; color: white; padding: 20px 30px;
            display: flex; align-items: center; gap: 12px;
        }
        header h1 { font-size: 1.4rem; }
        .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        .card {
            background: white; border-radius: 10px; padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .card h2 { font-size: 1.1rem; margin-bottom: 16px; color: #1a1a2e; border-bottom: 2px solid #e8e8e8; padding-bottom: 10px; }
        label { display: block; font-size: 0.85rem; font-weight: bold; margin-bottom: 4px; margin-top: 12px; color: #555; }
        input, select {
            width: 100%; padding: 9px 12px; border: 1px solid #ddd;
            border-radius: 6px; font-size: 0.9rem;
        }
        input:focus, select:focus { border-color: #4a90d9; outline: none; }
        button {
            margin-top: 16px; width: 100%; padding: 11px;
            background: #1a1a2e; color: white; border: none;
            border-radius: 6px; font-size: 0.95rem; cursor: pointer;
        }
        button:hover { background: #16213e; }
        button.warning { background: #e67e22; }
        button.warning:hover { background: #d35400; }
        .nav-links { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
        .nav-links a {
            padding: 10px 18px; background: white; border-radius: 8px;
            text-decoration: none; color: #1a1a2e; font-size: 0.9rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1); font-weight: bold;
        }
        .nav-links a:hover { background: #1a1a2e; color: white; }
        .respuesta { margin-top: 16px; padding: 12px; border-radius: 6px; font-size: 0.88rem; display: none; }
        .ok { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .err { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .full-width { grid-column: 1 / -1; }
        table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
        th { background: #1a1a2e; color: white; padding: 10px 12px; text-align: left; }
        td { padding: 9px 12px; border-bottom: 1px solid #eee; }
        tr:hover td { background: #f8f9fa; }
        .badge-ok { background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 12px; font-size: 0.78rem; }
        .badge-warn { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 12px; font-size: 0.78rem; }
        .badge-danger { background: #f8d7da; color: #721c24; padding: 2px 8px; border-radius: 12px; font-size: 0.78rem; }
        #loader { display: none; text-align: center; padding: 14px; color: #555; font-size: 0.9rem; }
        .spinner {
            border: 3px solid #f3f3f3; border-top: 3px solid #1a1a2e;
            border-radius: 50%; width: 22px; height: 22px;
            animation: spin 0.8s linear infinite; display: inline-block; margin-right: 8px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>

<header>
    <div>
        <h1>Sistema de Gestion de Inventario</h1>
        <small style="opacity:0.7;">TechNova Solutions - Dominio 3</small>
    </div>
</header>

<div class="container">

    <div class="nav-links">
        <a onclick="cargarStock()">Ver Stock Actual</a>
        <a onclick="cargarBajoStock()">Bajo Stock</a>
        <a onclick="cargarAlertas()">Alertas de Reposicion</a>
        <a onclick="cargarCategorias()">Categorias</a>
    </div>

    <div id="tabla-container" class="card full-width" style="display:none; margin-bottom:24px;">
        <h2 id="tabla-titulo">Datos</h2>
        <div id="loader"><div class="spinner"></div> Cargando...</div>
        <div id="tabla-contenido"></div>
    </div>

    <div class="grid">

        <div class="card">
            <h2>Registrar Producto</h2>
            <label>Nombre del producto</label>
            <input type="text" id="p-nombre" placeholder="Ej: Laptop HP 15">
            <label>Categoria</label>
            <select id="p-categoria">
                <option value="1">Electronica</option>
                <option value="2">Papeleria</option>
                <option value="3">Herramientas</option>
            </select>
            <label>Cantidad inicial</label>
            <input type="number" id="p-cantidad" value="10" min="0">
            <label>Precio unitario ($)</label>
            <input type="number" id="p-precio" value="100.00" min="0" step="0.01">
            <label>Stock minimo (umbral de alerta)</label>
            <input type="number" id="p-stock-min" value="5" min="1">
            <button onclick="registrarProducto()">Registrar Producto</button>
            <div id="resp-producto" class="respuesta"></div>
        </div>

        <div class="card">
            <h2>Registrar Movimiento</h2>
            <label>ID del Producto</label>
            <input type="number" id="m-producto-id" placeholder="Ej: 1" min="1">
            <label>Tipo de movimiento</label>
            <select id="m-tipo">
                <option value="entrada">Entrada (reposicion)</option>
                <option value="salida">Salida (venta / uso)</option>
            </select>
            <label>Cantidad</label>
            <input type="number" id="m-cantidad" value="1" min="1">
            <label>Motivo</label>
            <input type="text" id="m-motivo" placeholder="Ej: Venta a cliente, Reposicion mensual...">
            <button class="warning" onclick="registrarMovimiento()">Registrar Movimiento</button>
            <div id="loader-movimiento" style="display:none; margin-top:12px; text-align:center;">
                <div class="spinner"></div> Procesando... (puede tomar unos segundos si genera alerta)
            </div>
            <div id="resp-movimiento" class="respuesta"></div>
        </div>

    </div>

</div>

<script>
    function mostrarRespuesta(elId, mensaje, tipo) {
        const el = document.getElementById(elId);
        if (!el) return;
        el.style.display = 'block';
        el.className = 'respuesta ' + tipo;
        el.textContent = mensaje;
    }

    function mostrarTabla(titulo, html) {
        document.getElementById('tabla-container').style.display = 'block';
        document.getElementById('tabla-titulo').textContent = titulo;
        document.getElementById('loader').style.display = 'none';
        document.getElementById('tabla-contenido').innerHTML = html;
    }

    function mostrarLoader(titulo) {
        document.getElementById('tabla-container').style.display = 'block';
        document.getElementById('tabla-titulo').textContent = titulo;
        document.getElementById('loader').style.display = 'block';
        document.getElementById('tabla-contenido').innerHTML = '';
    }

    async function registrarProducto() {
        const body = {
            nombre: document.getElementById('p-nombre').value,
            categoria_id: parseInt(document.getElementById('p-categoria').value),
            cantidad: parseInt(document.getElementById('p-cantidad').value),
            precio: parseFloat(document.getElementById('p-precio').value),
            stock_minimo: parseInt(document.getElementById('p-stock-min').value)
        };
        try {
            const res = await fetch('/productos', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });
            const data = await res.json();
            mostrarRespuesta('resp-producto', res.ok ? data.mensaje : data.error, res.ok ? 'ok' : 'err');
        } catch(e) {
            mostrarRespuesta('resp-producto', 'Error de conexion: ' + e.message, 'err');
        }
    }

    async function registrarMovimiento() {
        const body = {
            producto_id: parseInt(document.getElementById('m-producto-id').value),
            tipo: document.getElementById('m-tipo').value,
            cantidad: parseInt(document.getElementById('m-cantidad').value),
            motivo: document.getElementById('m-motivo').value
        };
        document.getElementById('loader-movimiento').style.display = 'block';
        document.getElementById('resp-movimiento').style.display = 'none';
        try {
            const res = await fetch('/movimientos', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });
            const data = await res.json();
            document.getElementById('loader-movimiento').style.display = 'none';
            let msg = res.ok ? data.mensaje : data.error;
            if (data.alerta) msg += '\\n\\nALERTA: ' + data.alerta;
            mostrarRespuesta('resp-movimiento', msg, res.ok ? (data.alerta ? 'info' : 'ok') : 'err');
        } catch(e) {
            document.getElementById('loader-movimiento').style.display = 'none';
            mostrarRespuesta('resp-movimiento', 'Error de conexion: ' + e.message, 'err');
        }
    }

    async function cargarStock() {
        mostrarLoader('Stock Actual de Todos los Productos');
        try {
            const res = await fetch('/productos');
            const data = await res.json();
            if (!data.productos || data.productos.length === 0) {
                mostrarTabla('Stock Actual', '<p style="padding:12px;color:#888;">No hay productos registrados.</p>');
                return;
            }
            let html = '<table><thead><tr><th>ID</th><th>Nombre</th><th>Categoria</th><th>Stock</th><th>Min.</th><th>Precio</th><th>Estado</th></tr></thead><tbody>';
            data.productos.forEach(p => {
                const estado = p.cantidad <= p.stock_minimo
                    ? '<span class="badge-danger">Bajo</span>'
                    : '<span class="badge-ok">OK</span>';
                html += `<tr>
                    <td>${p.id}</td><td>${p.nombre}</td><td>${p.categoria}</td>
                    <td><strong>${p.cantidad}</strong></td><td>${p.stock_minimo}</td>
                    <td>$${parseFloat(p.precio).toFixed(2)}</td><td>${estado}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            mostrarTabla('Stock Actual (' + data.productos.length + ' productos)', html);
        } catch(e) {
            mostrarTabla('Error', '<p style="color:red;padding:12px;">Error al cargar: ' + e.message + '</p>');
        }
    }

    async function cargarBajoStock() {
        mostrarLoader('Productos por Debajo del Stock Minimo');
        try {
            const res = await fetch('/productos/bajo-stock');
            const data = await res.json();
            if (!data.productos || data.productos.length === 0) {
                mostrarTabla('Bajo Stock', '<p style="padding:12px;color:#28a745;">Todos los productos tienen stock suficiente.</p>');
                return;
            }
            let html = '<table><thead><tr><th>ID</th><th>Nombre</th><th>Stock Actual</th><th>Stock Minimo</th><th>Deficit</th><th>Precio</th></tr></thead><tbody>';
            data.productos.forEach(p => {
                const deficit = p.stock_minimo - p.cantidad;
                html += `<tr>
                    <td>${p.id}</td><td>${p.nombre}</td>
                    <td style="color:#dc3545;font-weight:bold;">${p.cantidad}</td>
                    <td>${p.stock_minimo}</td>
                    <td><span class="badge-danger">-${deficit} unidades</span></td>
                    <td>$${parseFloat(p.precio).toFixed(2)}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            mostrarTabla('Productos en Bajo Stock (' + data.productos.length + ')', html);
        } catch(e) {
            mostrarTabla('Error', '<p style="color:red;padding:12px;">Error: ' + e.message + '</p>');
        }
    }

    async function cargarAlertas() {
        mostrarLoader('Alertas de Reposicion');
        try {
            const res = await fetch('/alertas');
            const data = await res.json();
            if (!data.alertas || data.alertas.length === 0) {
                mostrarTabla('Alertas', '<p style="padding:12px;color:#28a745;">No hay alertas pendientes.</p>');
                return;
            }
            let html = '<table><thead><tr><th>ID</th><th>Producto</th><th>Stock al momento</th><th>Stock Minimo</th><th>Estado</th><th>Fecha</th></tr></thead><tbody>';
            data.alertas.forEach(a => {
                const badge = a.estado === 'pendiente'
                    ? '<span class="badge-warn">Pendiente</span>'
                    : '<span class="badge-ok">Atendida</span>';
                html += `<tr>
                    <td>${a.id}</td><td>${a.producto}</td>
                    <td style="color:#dc3545;"><strong>${a.stock_al_momento}</strong></td>
                    <td>${a.stock_minimo}</td><td>${badge}</td>
                    <td>${new Date(a.creado_en).toLocaleString('es-MX')}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            mostrarTabla('Alertas de Reposicion (' + data.alertas.length + ')', html);
        } catch(e) {
            mostrarTabla('Error', '<p style="color:red;padding:12px;">Error: ' + e.message + '</p>');
        }
    }

    async function cargarCategorias() {
        mostrarLoader('Categorias');
        try {
            const res = await fetch('/categorias');
            const data = await res.json();
            let html = '<table><thead><tr><th>ID</th><th>Nombre</th><th>Descripcion</th></tr></thead><tbody>';
            data.categorias.forEach(c => {
                html += `<tr><td>${c.id}</td><td>${c.nombre}</td><td>${c.descripcion || '-'}</td></tr>`;
            });
            html += '</tbody></table>';
            mostrarTabla('Categorias', html);
        } catch(e) {
            mostrarTabla('Error', '<p style="color:red;padding:12px;">Error: ' + e.message + '</p>');
        }
    }
</script>
</body>
</html>
"""


# Ruta 1 - Interfaz HTML principal
@app.route("/")
def index():
    return render_template_string(HTML_PRINCIPAL)


# Ruta 2 - Registrar un producto nuevo
@app.route("/productos", methods=["POST"])
def registrar_producto():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        # Validar que lleguen todos los campos necesarios
        campos_requeridos = ["nombre", "categoria_id", "cantidad", "precio", "stock_minimo"]
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido faltante: {campo}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar usando parametros para evitar inyeccion SQL
        sql = """
            INSERT INTO productos (nombre, categoria_id, cantidad, precio, stock_minimo)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data["nombre"],
            data["categoria_id"],
            data["cantidad"],
            data["precio"],
            data["stock_minimo"]
        ))
        conn.commit()

        return jsonify({
            "mensaje": f"Producto '{data['nombre']}' registrado correctamente con ID {cursor.lastrowid}.",
            "id": cursor.lastrowid
        }), 201

    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
    finally:
        # Siempre cerrar cursor y conexion
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Ruta 3 - Consultar stock actual de todos los productos
@app.route("/productos", methods=["GET"])
def consultar_stock():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # JOIN con categorias para traer el nombre en lugar del ID
        sql = """
            SELECT p.id, p.nombre, c.nombre AS categoria,
                   p.cantidad, p.precio, p.stock_minimo,
                   (p.cantidad <= p.stock_minimo) AS bajo_stock
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.nombre ASC
        """
        cursor.execute(sql)
        productos = cursor.fetchall()

        return jsonify({"productos": productos, "total": len(productos)}), 200

    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Ruta 4 - Registrar entrada o salida de inventario
@app.route("/movimientos", methods=["POST"])
def registrar_movimiento():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        # Validar campos requeridos
        campos_requeridos = ["producto_id", "tipo", "cantidad"]
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido faltante: {campo}"}), 400

        if data["tipo"] not in ("entrada", "salida"):
            return jsonify({"error": "El tipo debe ser 'entrada' o 'salida'."}), 400

        if data["cantidad"] <= 0:
            return jsonify({"error": "La cantidad debe ser mayor a 0."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener datos actuales del producto
        cursor.execute(
            "SELECT id, nombre, cantidad, stock_minimo FROM productos WHERE id = %s",
            (data["producto_id"],)
        )
        producto = cursor.fetchone()

        if not producto:
            return jsonify({"error": f"No existe un producto con ID {data['producto_id']}."}), 404

        # Calcular nuevo stock segun el tipo de movimiento
        if data["tipo"] == "entrada":
            nuevo_stock = producto["cantidad"] + data["cantidad"]
        else:
            nuevo_stock = producto["cantidad"] - data["cantidad"]
            if nuevo_stock < 0:
                return jsonify({
                    "error": f"Stock insuficiente. Stock actual: {producto['cantidad']}, intentas sacar: {data['cantidad']}."
                }), 400

        # Actualizar el stock en la tabla de productos
        cursor.execute(
            "UPDATE productos SET cantidad = %s WHERE id = %s",
            (nuevo_stock, data["producto_id"])
        )

        # Guardar el movimiento en el historial
        cursor.execute(
            """INSERT INTO movimientos (producto_id, tipo, cantidad, motivo, stock_resultante)
               VALUES (%s, %s, %s, %s, %s)""",
            (data["producto_id"], data["tipo"], data["cantidad"],
             data.get("motivo", "Sin motivo especificado"), nuevo_stock)
        )
        conn.commit()

        respuesta = {
            "mensaje": f"Movimiento registrado. Producto: '{producto['nombre']}' | Stock actualizado: {nuevo_stock}.",
            "stock_anterior": producto["cantidad"],
            "stock_actual": nuevo_stock,
            "alerta": None
        }

        # TAREA PESADA: si es salida y el stock queda bajo el minimo,
        # se genera una alerta de reposicion con time.sleep que simula
        # un proceso costoso como envio de notificaciones al proveedor.
        if data["tipo"] == "salida" and nuevo_stock <= producto["stock_minimo"]:
            print(f"[ALERTA] Iniciando proceso de reposicion para '{producto['nombre']}'...")

            # Simula el proceso costoso - minimo 5 segundos segun requisitos
            time.sleep(6)

            # Guardar la alerta en la base de datos
            cursor.execute(
                """INSERT INTO alertas_reposicion (producto_id, stock_al_momento, stock_minimo)
                   VALUES (%s, %s, %s)""",
                (data["producto_id"], nuevo_stock, producto["stock_minimo"])
            )
            conn.commit()
            print(f"[ALERTA] Alerta guardada para '{producto['nombre']}'.")

            respuesta["alerta"] = (
                f"Stock de '{producto['nombre']}' ({nuevo_stock} uds) esta por debajo del minimo "
                f"({producto['stock_minimo']} uds). Se genero una alerta de reposicion."
            )

        return jsonify(respuesta), 200

    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Ruta 5 - Productos por debajo del stock minimo
@app.route("/productos/bajo-stock", methods=["GET"])
def productos_bajo_stock():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Filtrar solo los productos cuyo stock es menor o igual al minimo
        sql = """
            SELECT p.id, p.nombre, c.nombre AS categoria,
                   p.cantidad, p.stock_minimo, p.precio
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE p.cantidad <= p.stock_minimo
            ORDER BY (p.stock_minimo - p.cantidad) DESC
        """
        cursor.execute(sql)
        productos = cursor.fetchall()

        return jsonify({
            "productos": productos,
            "total": len(productos),
            "mensaje": f"Se encontraron {len(productos)} productos con stock bajo."
        }), 200

    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Ruta 6 - Ver alertas de reposicion generadas
@app.route("/alertas", methods=["GET"])
def ver_alertas():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT a.id, p.nombre AS producto, a.stock_al_momento,
                   a.stock_minimo, a.estado, a.creado_en
            FROM alertas_reposicion a
            JOIN productos p ON a.producto_id = p.id
            ORDER BY a.creado_en DESC
        """
        cursor.execute(sql)
        alertas = cursor.fetchall()

        # Convertir fechas a string para que JSON las pueda serializar
        for alerta in alertas:
            if alerta["creado_en"]:
                alerta["creado_en"] = str(alerta["creado_en"])

        return jsonify({"alertas": alertas, "total": len(alertas)}), 200

    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Ruta 7 - Ver categorias disponibles
@app.route("/categorias", methods=["GET"])
def ver_categorias():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre")
        categorias = cursor.fetchall()

        return jsonify({"categorias": categorias}), 200

    except mysql.connector.Error as e:
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
