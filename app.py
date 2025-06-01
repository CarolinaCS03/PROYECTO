#------------------------------------
#EVA CAROLINA CEVALLOS SANCHEZ
#------------------------------------

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL


app = Flask(__name__)

#settings
app.secret_key = 'clave_secreta_segura'

#coneccion de mysql
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'opticatriem'
mysql = MySQL(app)


@app.route('/')
def carolina():
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM usuario')
  usuarios = cur.fetchall()
  cur.execute('SELECT * FROM compra')
  compras = cur.fetchall()
  cur.execute('SELECT * FROM venta')
  ventas = cur.fetchall()
  cur.execute('SELECT * FROM productos')
  productos = cur.fetchall()
  return render_template('index.html', usuarios=usuarios, compras=compras, ventas=ventas, productos=productos)


@app.route('/add_usuario', methods=['POST'])
def add_usuario():
    if request.method == 'POST':
        Cedula = request.form['Cedula']
        Nombre1 = request.form['Nombre1']
        Nombre2 = request.form['Nombre2']
        Apellido1 = request.form['Apellido1']
        Apellido2 = request.form['Apellido2']
        Telefono = request.form['Telefono']
        Direccion = request.form['Direccion']
        Correo = request.form['Correo']
        tipousuario = request.form['tipousuario']
        cur = mysql.connection.cursor()
        cur.execute('''
            INSERT INTO usuario 
            (Cedula, Nombre1, Nombre2, Apellido1, Apellido2, Telefono, Direccion, Correo, tipoUsuario) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (Cedula, Nombre1, Nombre2, Apellido1, Apellido2, Telefono, Direccion, Correo, tipousuario))
        mysql.connection.commit()
        flash('Se guardo completamente el registro')
        return redirect(url_for('carolina'))
    


@app.route('/add_compra', methods=['POST'])  
def add_compra():
    if request.method == 'POST':
        Distribuidor = request.form['Distribuidor']
        Empresa = request.form['Empresa']
        Descp = request.form['Descp']
        Costo = request.form['Costo']

        cur = mysql.connection.cursor()
        cur.execute('''
            INSERT INTO compra 
            (Distribuidor, Empresa, Descp, Costo) 
            VALUES (%s, %s, %s, %s)
        ''', (Distribuidor, Empresa, Descp, Costo))

        mysql.connection.commit()
        flash('Se guardó completamente la compra')
        return redirect(url_for('carolina'))


@app.route('/add_venta', methods=['POST'])  
def add_venta():
    if request.method == 'POST':
        NumFactura = request.form['NumFactura']
        Comprador = request.form['Comprador']
        Vendedor = request.form['Vendedor']
        PrecioTotal = request.form['PrecioTotal']
        IvaTotal = request.form['IvaTotal']

        cur = mysql.connection.cursor()
        cur.execute('''
            INSERT INTO venta
            (NumFactura, Comprador, Vendedor, PrecioTotal, IvaTotal) 
            VALUES (%s, %s, %s, %s, %s)
        ''', (NumFactura, Comprador, Vendedor, PrecioTotal, IvaTotal))

        mysql.connection.commit()

        cur2 = mysql.connection.cursor()
        cur2.execute('''
            INSERT INTO detalle_venta (VentaId, ProductoId, Cantidad, Precio)
            VALUES (%s, %s, %s, %s)
        ''', (cur.lastrowid, ProductoId, Cantidad, Precio))
        
        mysql.connection.commit()
        flash('Se guardó completamente la venta')
        return redirect(url_for('carolina'))
    

@app.route('/detalle_venta/<int:id>')
def detalle_venta(id):
    venta = obtener_venta_por_id(id)         # Diccionario con claves como 'NumFactura', 'Total', etc.
    detalles = obtener_detalles_venta(id)    # Lista de diccionarios con ProductoNombre, Cantidad, etc.
    return render_template('detalle_venta.html', venta=venta, detalles=detalles)


@app.route('/add_productos', methods=['POST'])
def add_productos():
    codigo = request.form['Codigo']
    tipo_lente = request.form['TipoLente']
    descripcion = request.form['Descripcion']
    stock = request.form['Stock']
    precio = request.form['Precio']

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO Productos (Codigo, TipoLente, Descripcion, Stock, Precio)
        VALUES (%s, %s, %s, %s, %s)
    """, (codigo, tipo_lente, descripcion, stock, precio))
    mysql.connection.commit()
    flash('Producto agregado correctamente')
    return redirect(url_for('carolina'))



    
    
@app.route('/update_usuario/<int:id>', methods=['POST'])
def update_usuario(id):
    cedula = request.form['Cedula']
    nombre1 = request.form['Nombre1']
    nombre2 = request.form['Nombre2']
    apellido1 = request.form['Apellido1']
    apellido2 = request.form['Apellido2']
    telefono = request.form['Telefono']
    direccion = request.form['Direccion']
    correo = request.form['Correo']
    tipousuario = request.form['tipousuario']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE usuario SET
        Cedula=%s, Nombre1=%s, Nombre2=%s, Apellido1=%s,
        Apellido2=%s, Telefono=%s, Direccion=%s, Correo=%s,
        tipoUsuario=%s WHERE id=%s
    """, (cedula, nombre1, nombre2, apellido1, apellido2,
          telefono, direccion, correo, tipousuario, id))
    mysql.connection.commit()
    flash('Usuario actualizado correctamente')
    return redirect(url_for('carolina'))


@app.route('/update_compra/<int:id>', methods=['POST'])
def update_compra(id):
    distribuidor = request.form['Distribuidor']
    empresa = request.form['Empresa']
    descp = request.form['Descp']
    costo = request.form['Costo']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE compra SET
        Distribuidor=%s, Empresa=%s, Descp=%s,
        Costo=%s WHERE id=%s
    """, (distribuidor, empresa, descp, costo, id))
    mysql.connection.commit()
    flash('Compra actualizada correctamente')
    return redirect(url_for('carolina'))



@app.route('/update_venta/<int:id>', methods=['POST'])
def update_venta(id):
    numfactura = request.form['NumFactura']
    comprador = request.form['Comprador']
    vendedor = request.form['Vendedor']
    preciototal = request.form['PrecioTotal']
    ivatotal = request.form['IvaTotal']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE venta SET
        NumFactura=%s, Comprador=%s, Vendedor=%s,
        PrecioTotal=%s, IvaTotal=%s WHERE id=%s
    """, (numfactura, comprador, vendedor, preciototal, ivatotal, id))
    mysql.connection.commit()
    flash('Venta actualizada correctamente')
    return redirect(url_for('carolina'))


@app.route('/update_productos/<int:id>', methods=['POST'])
def update_productos(id):
    codigo = request.form['Codigo']           # campo que envía el formulario para Código
    precio = request.form['Precio']
    stock = request.form['Stock']              # campo para Stock (cantidad)
    descripcion = request.form['Descripcion']
    tipo_lente = request.form['TipoLente']    # si tienes este campo en el formulario

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE Productos SET
        Codigo=%s,
        Precio=%s,
        Stock=%s,
        Descripcion=%s,
        TipoLente=%s
        WHERE Id=%s
    """, (codigo, precio, stock, descripcion, tipo_lente, id))
    mysql.connection.commit()
    flash('Producto actualizado correctamente')
    return redirect(url_for('carolina'))



@app.route('/edit_usuario/<id>')
def get_usuario(id):
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM usuario WHERE id = %s', (id,))
  data = cur.fetchall()
  return render_template('edit_usuario.html', usuario = data[0])
 


@app.route('/delete_usuario/<string:id>')
def delete_usuario(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM usuario WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Usuario eliminado')
    return redirect(url_for('carolina'))


@app.route('/edit_compra/<id>')
def get_compra(id):
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM compra WHERE id = %s', (id,))
  data = cur.fetchall()
  return render_template('edit_compra.html', compra = data[0])

@app.route('/delete_compra/<string:id>')
def delete_compra(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM compra WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Compra eliminada')
    return redirect(url_for('carolina'))

@app.route('/edit_venta/<id>')
def get_venta(id):
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM venta WHERE id = %s', (id,))
  data = cur.fetchall()
  return render_template('edit_venta.html', venta = data[0])

@app.route('/delete_venta/<string:id>')
def delete_venta(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM venta WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Venta eliminada')
    return redirect(url_for('carolina'))

@app.route('/edit_productos/<id>')
def get_productos(id):
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM productos WHERE id = %s', (id,))
  data = cur.fetchall()
  return render_template('edit_productos.html', producto = data[0])

@app.route('/delete_productos/<string:id>')
def delete_productos(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM productos WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Producto eliminado')
    return redirect(url_for('carolina'))


def obtener_venta_por_id(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM venta WHERE id = %s', (id,))
    venta = cur.fetchone()
    return venta


def obtener_detalles_venta(id_venta):
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT p.Descripcion AS NombreProducto,
               dv.Cantidad,
               dv.PrecioUnitario,
               (dv.PrecioUnitario * dv.Cantidad) AS PrecioTotal,
               (dv.PrecioUnitario * dv.Cantidad * 0.12) AS IVA
        FROM detalleventa dv
        JOIN Productos p ON dv.Productoid = p.Id
        WHERE dv.VentaId = %s
    ''', (id_venta,))
    detalles = cur.fetchall()
    print(detalles)
    return detalles




if __name__ == '__main__':
  app.run(port = 5000, debug = True)
