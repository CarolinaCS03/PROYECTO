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

