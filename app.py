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


@app.route('/generar_factura/<int:id>')
def generar_factura(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT pagos.id, pagos.monto, pagos.fecha_pago, pagos.estado_pago, 
                   IFNULL(clientes.nombres, 'Carolina Cevallos'), 
                   IFNULL(clientes.correo, 'CarolinaCevallos@gmail')
            FROM pagos 
            LEFT JOIN ventas ON pagos.id_venta = ventas.id
            LEFT JOIN clientes ON TRIM(ventas.cedula) = TRIM(clientes.cedula)
            WHERE pagos.id = %s
        """, (id,))
        pago = cur.fetchone()

        if not pago:
            flash('Pago no encontrado', 'error')
            return redirect(url_for('pagos'))

        pdf = FPDF()
        pdf.add_page()

        # Colores base
        rosa_banner = (255, 192, 203)
        gris_texto = (80, 80, 80)
        fondo_detalle = (255, 230, 240)
        lila = (186, 85, 211)

        # Encabezado con banner rosa
        pdf.set_fill_color(*rosa_banner)
        pdf.rect(0, 0, 210, 30, 'F')
        if os.path.exists("static/img/logoe.jpg"):
            pdf.image("static/img/logoe.jpg", x=10, y=5, w=20)
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(35, 10)
        pdf.cell(140, 10, "Óptica Triem - Belleza y Salud Visual", ln=False, align="C")

        pdf.set_y(35)
        pdf.set_text_color(*gris_texto)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, "Dirección: Av Rocafuerte y Juan Pablo Segundo - Portoviejo", ln=True, align="L")
        pdf.cell(0, 5, "Email: opticatriem100@gmail.com | Tel: +593 982 566 014", ln=True, align="L")
        pdf.ln(5)

        # Sección Datos (2 columnas)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(100, 8, "Datos del Cliente", ln=0)
        pdf.cell(0, 8, "Datos de la Factura", ln=1)

        pdf.set_font("Arial", "", 11)
        pdf.cell(100, 8, f"Nombre: {pago[4]}", ln=0)
        pdf.cell(0, 8, f"Número: {pago[0]}", ln=1)
        pdf.cell(100, 8, f"Correo: {pago[5]}", ln=0)
        pdf.cell(0, 8, f"Fecha: {pago[2]}", ln=1)
        pdf.ln(10)

        # Detalle de pago (tabla)
        pdf.set_fill_color(*fondo_detalle)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(40, 10, "Cantidad", 1, 0, "C", True)
        pdf.cell(80, 10, "Descripción", 1, 0, "C", True)
        pdf.cell(40, 10, "Precio Venta.", 1, 0, "C", True)
        pdf.cell(30, 10, "Total", 1, 1, "C", True)

        pdf.set_font("Arial", "", 11)
        pdf.cell(40, 10, "1", 1, 0, "C")
        pdf.cell(80, 10, "Pago por venta óptica", 1, 0)
        pdf.cell(40, 10, f"${pago[1]:.2f}", 1, 0, "C")
        pdf.cell(30, 10, f"${pago[1]:.2f}", 1, 1, "C")
        pdf.ln(10)

        # Total destacado
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(*lila)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(160, 10, "TOTAL A PAGAR", 1, 0, "R", True)
        pdf.cell(30, 10, f"${pago[1]:.2f}", 1, 1, "C", True)
        pdf.set_text_color(*gris_texto)
        pdf.ln(15)

        # Footer boutique
        pdf.set_font("Arial", "I", 10)
        pdf.set_text_color(150, 75, 150)
        pdf.cell(0, 10, "Gracias por tu compra bella. ¡Tu mirada es nuestro compromiso!", ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 10, "Factura digital generada automáticamente.", ln=True, align="C")

        # Exportar
        pdf_file = "factura.pdf"
        pdf.output(pdf_file)

        return send_file(pdf_file, as_attachment=True, download_name="factura.pdf")

    except Exception as e:
        flash(f"Error al generar la factura: {str(e)}", 'error')
        return redirect(url_for('pagos'))


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
        precio_total = request.form['precio_total']
        iva_total = request.form['iva_total']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO ventas (cedula, precio_total, iva_total) 
            VALUES (%s, %s, %s)
""", (cedula, precio_total, iva_total))

        mysql.connection.commit()
        flash('venta agregado correctamente')
        return redirect(url_for('ventas'))
    
@app.route('/editar_venta/<int:id>', methods=['GET', 'POST'])
def editar_venta(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ventas WHERE id = %s", [id])
    venta = cur.fetchone()
    cur.close()

    if not venta:
        return redirect(url_for('ventas'))

    if request.method == 'POST':
        cedula = request.form['cedula']
        precio_total = request.form['precio_total']
        iva_total = request.form['iva_total']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE ventas 
            SET cedula = %s, precio_total = %s, iva_total = %s
            WHERE id = %s
        """, (cedula, precio_total, iva_total, id))
        mysql.connection.commit()
        cur.close()

        flash('Venta actualizado correctamente')
        return redirect(url_for('ventas'))

    return render_template('editar_venta.html', venta=venta)

@app.route('/eliminar_venta/<int:id>', methods=['POST'])
def eliminar_venta(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM ventas WHERE id = %s', (id,))
    mysql.connection.commit()  # Confirmar la eliminación
    flash('Venta eliminado correctamente')
    return redirect(url_for('ventas'))

@app.route('/detalle_venta/<int:id>')
def detalle_venta(id):
    cur = mysql.connection.cursor()

    # Obtener datos de la venta
    cur.execute('SELECT id, cedula, precio_total, iva_total FROM ventas WHERE id = %s', (id,))
    venta = cur.fetchone()

    if not venta:
        flash('Venta no encontrada.')
        return redirect(url_for('ventas'))

    venta_data = {
        'id': venta[0],
        'cedula': venta[1],  # Asumimos que contiene el ID del producto
        'precio_total': venta[2],
        'iva_total': venta[3]
    }

    # Obtener datos del cliente
    cur.execute('SELECT nombres, apellidos, telefono FROM clientes WHERE cedula = %s', (venta_data['cedula'],))
    cliente = cur.fetchone()
    cliente_data = {
        'nombres': cliente[0],
        'apellidos': cliente[1],
        'telefono': cliente[2]
    } if cliente else None

    # Obtener datos del producto (desde detalle_venta como ID)
    try:
        cur.execute("SELECT tipo_lente, descripcion, precio FROM productos WHERE id = %s", (5,))  # <- usa un producto temporal
        producto = cur.fetchone()
        productos_data = []
        if producto:
            productos_data.append({
                'tipo_lente': producto[0],
                'descripcion': producto[1],
                'precio': producto[2]
    }) if producto else []
    except:
        productos_data = []

    cur.close()

    return render_template('detalle_venta.html', venta=venta_data, cliente=cliente_data, productos=productos_data)

# ----------------------- PAGOS -----------------------
@app.route('/pagos')
def pagos():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, id_venta, monto, fecha_pago, estado_pago FROM pagos')
    data = cur.fetchall()
    pagos = [{'id': row[0], 'id_venta': row[1], 'monto': row[2], 'fecha_pago': row[3], 'estado_pago': row[4]} for row in data]
    cur.close()
    return render_template('tabla_pagos.html', pagos=pagos)


@app.route('/pagos/add', methods=['POST'])
def add_pago():
    if request.method == 'POST':
        try:
            id_venta = request.form['id_venta']
            monto = request.form['monto']
            fecha_pago = request.form['fecha_pago']
            estado_pago = request.form['estado_pago']
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO pagos (id_venta, monto, fecha_pago, estado_pago) 
                VALUES (%s, %s, %s, %s)
            """, (id_venta, monto, fecha_pago, estado_pago))

            mysql.connection.commit()
            flash('Pago registrado correctamente')
        except Exception as e:
            flash('Error al agregar el pago: verifica que el ID de la reserva sea válido.', 'error')
    return redirect(url_for('pagos'))
    
@app.route('/editar_pago/<int:id>', methods=['GET', 'POST'])
def editar_pago(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pagos WHERE id = %s", [id])
    pago = cur.fetchone()
    cur.close()

    if not pago:
        return redirect(url_for('pagos'))

    if request.method == 'POST':
        id_venta = request.form['id_venta']
        monto = request.form['monto']
        fecha_pago = request.form['fecha_pago']
        estado_pago = request.form['estado_pago']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE pagos 
            SET id_venta = %s, monto = %s, fecha_pago = %s, estado_pago = %s 
            WHERE id = %s
        """, (id_venta, monto, fecha_pago, estado_pago, id))
        mysql.connection.commit()
        cur.close()

        flash('Pago registrado correctamente')
        return redirect(url_for('pagos'))

    return render_template('editar_pago.html', pago=pago)

@app.route('/eliminar_pago/<int:id>', methods=['POST'])
def eliminar_pago(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM pagos WHERE id = %s', (id,))
    mysql.connection.commit()  # Confirmar la eliminación
    flash('Pago eliminado correctamente')
    return redirect(url_for('pagos'))

# ----------------------- PRODUCTOS -----------------------
@app.route('/productos')
def productos():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, tipo_lente, descripcion, stock, precio FROM productos')
    data = cur.fetchall()
    productos = [{'id': row[0], 'tipo_lente': row[1], 'descripcion': row[2], 'stock': row[3], 'precio': row[4]} for row in data]
    cur.close()
    return render_template('tabla_productos.html', productos=productos )

@app.route('/productos/add', methods=['POST'])
def add_producto():
    if request.method == 'POST':
        tipo_lente = request.form['tipo_lente']
        descripcion = request.form['descripcion']
        stock = request.form['stock']
        precio = request.form['precio']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO productos (tipo_lente, descripcion, stock, precio) 
            VALUES (%s, %s, %s, %s)
""", (tipo_lente, descripcion, stock, precio))

        mysql.connection.commit()
        flash('producto agregado correctamente')
        return redirect(url_for('productos'))
    
@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos WHERE id = %s", [id])
    producto = cur.fetchone()
    cur.close()

    if not producto:
        return redirect(url_for('productos'))

    if request.method == 'POST':
        tipo_lente = request.form['tipo_lente']
        descripcion = request.form['descripcion']
        stock = request.form['stock']
        precio = request.form['precio']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE productos 
            SET tipo_lente = %s, descripcion = %s, stock = %s, precio = %s
            WHERE id = %s
        """, (tipo_lente, descripcion, stock, precio, id))
        mysql.connection.commit()
        cur.close()

        flash('Producto actualizado correctamente')
        return redirect(url_for('productos'))

    return render_template('editar_producto.html', producto=producto)

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM productos WHERE id = %s', (id,))
    mysql.connection.commit()  # Confirmar la eliminación
    flash('Producto eliminado correctamente')
    return redirect(url_for('productos'))

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3000)