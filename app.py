#--------------------------------------------------------
#CATAGUA CAMACHO NAYELI ALEXANDRA
#CEVALLOS SANCHEZ EVA CAROLINA
#DUEÑAS GARCIA JENIFFER YUSBELY
#SOLORZANO CHAVEZ DANIELA THAIZ
#--------------------------------------------------------

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from flask import send_file
from fpdf import FPDF
import os
from MySQLdb.cursors import DictCursor  #

load_dotenv()
app = Flask(__name__)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  
app.config['MYSQL_DB'] = 'opticatr'
app.secret_key = '1234'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

mysql = MySQL(app)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# ----------------------- COMPRAS -----------------------
@app.route('/compras')
def compras():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, distribuidor, empresa, descripcion, costo FROM compras")
    data = cur.fetchall()
    # Convertir a una lista de diccionarios
    compras = [{'id': row[0], 'distribuidor': row[1], 'empresa': row[2], 'descripcion': row[3], 'costo': row[4]} for row in data]
    cur.close()
    return render_template('tabla_compras.html', compras=compras)

@app.route('/compras/add', methods=['POST'])
def add_compra():
    if request.method == 'POST':
        distribuidor = request.form['distribuidor']
        empresa = request.form['empresa']
        descripcion = request.form['descripcion']
        costo = request.form['costo']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO compras (distribuidor, empresa, descripcion, costo) 
            VALUES (%s, %s, %s, %s)
""", (distribuidor, empresa , descripcion, costo))

        mysql.connection.commit()
        flash('compra agregada correctamente')
        return redirect(url_for('compras'))
    
@app.route('/editar_compra/<int:id>', methods=['GET', 'POST'])
def editar_compra(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM compras WHERE id = %s", [id])
    compra = cur.fetchone()
    cur.close()

    if not compra:
        return redirect(url_for('compras'))

    if request.method == 'POST':
        distribuidor = request.form['distribuidor']
        empresa = request.form['empresa']
        descripcion = request.form['descripcion']
        costo = request.form['costo']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE compras 
            SET distribuidor = %s, empresa = %s, descripcion = %s, costo = %s
            WHERE id = %s
        """, (distribuidor, empresa, descripcion, costo, id))
        mysql.connection.commit()
        cur.close()

        flash('compra actualizada correctamente')
        return redirect(url_for('compras'))

    return render_template('editar_compra.html', compra=compra)

@app.route('/eliminar_compra/<int:id>', methods=['POST'])
def eliminar_compra(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM compras WHERE id = %s', (id,))
    mysql.connection.commit()  # Confirmar la eliminación
    flash('Compra eliminada correctamente')
    return redirect(url_for('compras'))

# ----------------------- CLIENTES -----------------------
@app.route('/clientes')
def clientes():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, cedula, nombres, apellidos, telefono, direccion, correo FROM clientes')
    data = cur.fetchall()
    clientes = [{'id': row[0], 'cedula': row[1], 'nombres': row[2], 'apellidos': row[3], 'telefono': row[4], 'direccion': row[5], 'correo': row[6]} for row in data]
    cur.close()
    return render_template('tabla_clientes.html', clientes=clientes)


@app.route('/clientes/add', methods=['POST'])
def add_cliente():
    if request.method == 'POST':
        cedula = request.form['cedula']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        correo = request.form['correo']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO clientes (cedula, nombres, apellidos, telefono, direccion, correo) VALUES (%s, %s, %s, %s, %s, %s)", (cedula, nombres, apellidos, telefono, direccion, correo))
        mysql.connection.commit()
        flash('Cliente agregado correctamente')
        return redirect(url_for('clientes'))
    
@app.route('/buscar_cliente', methods=['GET'])
def buscar_cliente():
    cedula = request.args.get('cedula')
    cur = mysql.connection.cursor()
    cur.execute("SELECT nombres, apellidos, telefono FROM clientes WHERE cedula = %s", (cedula,))
    data = cur.fetchone()
    cur.close()

    if data:
        return jsonify({
            'nombres': data[0],
            'apellidos': data[1],
            'telefono': data[2]
        })
    else:
        return jsonify({'error': 'Cliente no encontrado'}), 404

    
@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM clientes WHERE id = %s", [id])
    cliente = cur.fetchone()
    cur.close()

    if not cliente:
        return redirect(url_for('clientes'))

    if request.method == 'POST':
        cedula = request.form['cedula']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        correo = request.form['correo']
        

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE clientes 
            SET cedula = %s, nombres = %s, apellidos = %s, telefono = %s, direccion = %s, correo = %s
            WHERE id = %s
        """, (cedula, nombres, apellidos, telefono, direccion, correo, id))
        mysql.connection.commit()
        cur.close()

        flash('Cliente actualizado correctamente')
        return redirect(url_for('clientes'))

    return render_template('editar_cliente.html', cliente=cliente)    
    

@app.route('/eliminar_cliente/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM clientes WHERE id = %s', (id,))
    mysql.connection.commit()  # Confirmar la eliminación
    flash('Cliente eliminado correctamente')
    return redirect(url_for('clientes'))

# ----------------------- FACTURAS -----------------------
@app.route('/generar_factura/<int:pago_id>')
def generar_factura(pago_id):
    cur = mysql.connection.cursor(DictCursor)

    # 1. Datos del pago, venta y cliente
    cur.execute("""
        SELECT pg.id AS pago_id, pg.monto, pg.fecha_pago, pg.estado_pago,
               v.id AS venta_id, v.precio_total AS venta_total, v.iva_total AS venta_iva,
               IFNULL(c.nombres, 'Cliente sin nombre') AS nombres,
               IFNULL(c.apellidos, '') AS apellidos,
               IFNULL(c.correo, 'sin_correo@demo.com') AS correo
        FROM pagos pg
        JOIN ventas v ON v.id = pg.id_venta
        LEFT JOIN clientes c ON TRIM(v.cedula) = TRIM(c.cedula)
        WHERE pg.id = %s
    """, (pago_id,))
    pago = cur.fetchone()

    if not pago:
        return "Pago no encontrado", 404

    venta_id = pago['venta_id']

    # 2. Productos
    cur.execute("""
        SELECT p.tipo_lente, p.descripcion,
               dv.precio_unitario, dv.iva_unitario
        FROM detalle_venta dv
        JOIN productos p ON p.id = dv.id_producto
        WHERE dv.id_venta = %s
    """, (venta_id,))
    productos = cur.fetchall()

    # 3. Total pagado acumulado si está pendiente
    monto_pagado = pago['monto']
    monto_faltante = 0
    if pago['estado_pago'].lower() == 'pendiente':
        cur.execute("""
            SELECT SUM(monto) AS total_pagado
            FROM pagos
            WHERE id_venta = %s
        """, (venta_id,))
        resultado = cur.fetchone()
        monto_pagado = resultado['total_pagado'] or 0
        monto_faltante = pago['venta_total'] - monto_pagado

    # 4. Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Colores
    azul = (50, 130, 184)
    gris = (230, 230, 230)

    # Encabezado
    pdf.set_fill_color(*azul)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 15, "Optica Triem - Factura de Venta", ln=True, align='C', fill=True)

    pdf.set_text_color(0)
    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    pdf.cell(0, 10, f"Factura No: {pago['pago_id']}", ln=True)
    pdf.cell(0, 8, f"Fecha de Pago: {pago['fecha_pago']}", ln=True)
    pdf.cell(0, 8, f"Estado del Pago: {pago['estado_pago']}", ln=True)

    # Cliente
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Informacion del Cliente:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Nombre: {pago['nombres']} {pago['apellidos']}", ln=True)
    pdf.cell(0, 8, f"Correo: {pago['correo']}", ln=True)

    # Linea divisoria
    pdf.ln(3)
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    # Tabla de productos
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(*gris)
    pdf.cell(80, 10, "Producto", border=1, fill=True)
    pdf.cell(30, 10, "Precio", border=1, fill=True)
    pdf.cell(30, 10, "IVA", border=1, fill=True)
    pdf.cell(50, 10, "Total", border=1, ln=True, fill=True)

    pdf.set_font("Arial", '', 11)
    total = 0
    iva_total = 0
    fill = False
    for p in productos:
        texto = f"{p['tipo_lente']} - {p['descripcion']}"
        precio = p['precio_unitario']
        iva = p['iva_unitario']
        subtotal = precio + iva
        total += precio
        iva_total += iva

        pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(80, 10, texto, border=1, fill=fill)
        pdf.cell(30, 10, f"${precio:.2f}", border=1, fill=fill)
        pdf.cell(30, 10, f"${iva:.2f}", border=1, fill=fill)
        pdf.cell(50, 10, f"${subtotal:.2f}", border=1, ln=True, fill=fill)
        fill = not fill

    # Totales
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(140, 10, "Subtotal:", border=0)
    pdf.cell(50, 10, f"${total:.2f}", ln=True)
    pdf.cell(140, 10, "IVA Total:", border=0)
    pdf.cell(50, 10, f"${iva_total:.2f}", ln=True)
    pdf.cell(140, 10, "Total Venta:", border=0)
    pdf.cell(50, 10, f"${pago['venta_total']:.2f}", ln=True)

    # Mostrar valores pendientes
    if pago['estado_pago'].lower() == 'pendiente':
        pdf.cell(140, 10, "Total Pagado:", border=0)
        pdf.cell(50, 10, f"${monto_pagado:.2f}", ln=True)
        pdf.cell(140, 10, "Falta por Pagar:", border=0)
        pdf.cell(50, 10, f"${monto_faltante:.2f}", ln=True)

    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100)
    pdf.cell(0, 10, "Gracias por su compra. Vuelva pronto", ln=True, align='C')

    # Guardar PDF y devolver
    nombre_pdf = "factura.pdf"
    pdf.output(nombre_pdf)
    return send_file(nombre_pdf, as_attachment=True)

# ----------------------- VENTAS -----------------------
@app.route('/ventas')
def ventas():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, cedula, precio_total, iva_total FROM ventas')
    data = cur.fetchall()
    ventas = [{'id': row[0], 'cedula': row[1], 'precio_total': row[2], 'iva_total': row[3]} for row in data]
    cur.close()
    return render_template('tabla_ventas.html', ventas=ventas)


@app.route('/ventas/add', methods=['POST'])
def add_venta():
    if request.method == 'POST':
        cedula = request.form['cedula']
        subtotal = float(request.form['subtotal'])
        iva_total = float(request.form['iva_total'])
        precio_total = float(request.form['precio_total'])
        productos_str = request.form['productos[]']
        productos = productos_str.split(',') if productos_str else []       
        # 1. Insertar la venta
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO ventas (cedula, precio_total, iva_total) 
            VALUES (%s, %s, %s)
        """, (cedula, precio_total, iva_total))

        id_venta = cur.lastrowid  # Obtener el ID de la venta recién insertada

        # 2. Insertar los detalles de la venta
        print(productos)
        for producto_id in productos:
            # Obtener precio e IVA del producto actual desde la BD
            cur.execute("SELECT precio_base, iva_total FROM productos WHERE id = %s", (producto_id,))
            producto = cur.fetchone()

            if producto:
                precio = producto[0]
                iva = producto[1]
                cantidad = 1  # podrías tomarla de `cantidades` si se usa

                cur.execute("""
                    INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, iva_unitario)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_venta, producto_id, cantidad, precio, iva))

        mysql.connection.commit()
        flash('Venta y detalle de venta agregados correctamente')
        return redirect(url_for('ventas'))
    
# ----------------------- EDITAR VENTAS -----------------------
@app.route('/editar_venta/<int:id>', methods=['GET', 'POST'])
def editar_venta(id):
    conn = mysql.connection
    cur = conn.cursor()

    # ─── 1. Obtener cabecera ───
    cur.execute("SELECT id, cedula, precio_total, iva_total FROM ventas WHERE id=%s", (id,))
    row = cur.fetchone()
    if not row:
        flash("Venta no encontrada", "danger")
        return redirect(url_for('ventas'))

    venta = {
        "id": row[0],
        "cedula": row[1],
        "precio_total": float(row[2]),
        "iva_total": float(row[3])
    }

    # ─── 2. Obtener detalles ───
    cur.execute("""
        SELECT dv.id_producto,
               p.tipo_lente,
               dv.precio_unitario,
               dv.iva_unitario
        FROM detalle_venta dv
        JOIN productos p ON p.id = dv.id_producto
        WHERE dv.id_venta = %s
    """, (id,))
    detalles = cur.fetchall()

    productos_previos = [
        {
            "id_producto": d[0],
            "nombre": d[1],
            "precio_unitario": float(d[2]),
            "iva_unitario": float(d[3])
        } for d in detalles
    ]

    if request.method == 'POST':
        cedula = request.form['cedula']
        precio_total = float(request.form['precio_total'])
        iva_total = float(request.form['iva_total'])

        cur.execute("""
            UPDATE ventas
               SET cedula=%s,
                   precio_total=%s,
                   iva_total=%s
             WHERE id=%s
        """, (cedula, precio_total, iva_total, id))

        cur.execute("DELETE FROM detalle_venta WHERE id_venta=%s", (id,))

        total_prod = int(request.form['total_productos'])
        for i in range(total_prod):
            prod_id = int(request.form[f'producto_id_{i}'])
            precio = float(request.form[f'precio_{i}'])
            iva = float(request.form[f'iva_{i}'])

            cur.execute("""
                INSERT INTO detalle_venta
                       (id_venta, id_producto, cantidad, precio_unitario, iva_unitario)
                VALUES (%s, %s, 1, %s, %s)
            """, (id, prod_id, precio, iva))

        conn.commit()
        cur.close()
        flash("Venta actualizada correctamente", "success")
        return redirect(url_for('ventas'))

    subtotal_front = venta["precio_total"] - venta["iva_total"]

    cur = conn.cursor()
    cur.execute("SELECT id, tipo_lente, precio_base, iva_total FROM productos")
    todos_lentes = [
        {"id": r[0], "tipo_lente": r[1], "precio": float(r[2]), "iva": float(r[3])}
        for r in cur.fetchall()
    ]
    cur.close()

    return render_template(
        "editar_venta.html",
        venta=venta,
        subtotal_front=f"{subtotal_front:.2f}",
        productos_previos=productos_previos,
        todos_lentes=todos_lentes
    )



@app.route('/eliminar_venta/<int:id>', methods=['POST'])
def eliminar_venta(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM ventas WHERE id = %s', (id,))
    mysql.connection.commit()  # Confirmar la eliminación
    flash('Venta eliminado correctamente')
    return redirect(url_for('ventas'))

@app.route("/detalle_venta/<int:id>")
def detalle_venta(id):
    cur = mysql.connection.cursor()
    
    # Obtener datos de la venta y su cliente
    cur.execute("""
        SELECT v.id, v.cedula, c.nombres, c.apellidos, c.telefono,
               v.precio_total, v.iva_total
        FROM ventas v
        JOIN clientes c ON v.cedula = c.cedula
        WHERE v.id = %s
    """, (id,))
    row = cur.fetchone()
    if not row:
        return "Venta no encontrada", 404
    
    cols = [col[0] for col in cur.description]
    venta = dict(zip(cols, row))
    
    # Obtener productos relacionados con la venta desde tabla 'detalle_venta'
    cur.execute("""
        SELECT p.tipo_lente,
               dv.precio_unitario,
               dv.iva_unitario,
               (dv.precio_unitario * dv.cantidad) AS total_unitario
        FROM detalle_venta dv
        JOIN productos p ON dv.id_producto = p.id
        WHERE dv.id_venta = %s
    """, (id,))
    rows = cur.fetchall()

    productos = [dict(zip([col[0] for col in cur.description], row)) for row in rows]
    

    cur.close()
    for p in productos:
        p['precio_unitario'] = p['precio_unitario'] or 0
        p['iva_unitario'] = p['iva_unitario'] or 0
    print(productos)
    return render_template('detalle_venta.html', venta=venta, productos=productos)
