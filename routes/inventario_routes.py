from flask import render_template, request, redirect, url_for, flash
from datetime import datetime

class InventarioRoutes:
    def __init__(self, app, mysql):
        self.app = app
        self.mysql = mysql
        self.add_routes()
    
    def add_routes(self):
        @self.app.route('/inventario')
        def inventario():
            cur = self.mysql.connection.cursor()
            cur.execute("SELECT * FROM inventario")
            inventarios = cur.fetchall()
            cur.execute("SELECT * FROM producto")
            producto = cur.fetchall()
            cur.execute("""SELECT ip.id_inventario, i.nombre_inventario, p.nombre, p.cantidad
                FROM inventario_producto ip
                JOIN producto p ON ip.referencia = p.referencia
                JOIN inventario i ON ip.id_inventario = i.id_inventario""")
            inventario_producto = cur.fetchall()
            return render_template('inventario.html', inventarios=inventarios, producto=producto, inventario_producto=inventario_producto)

        @self.app.route('/add_inventario', methods=['POST'])
        def add_inventario():
            if request.method == 'POST':
                nombre = request.form['nombre']
                fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                notas = request.form['notas']
                cur = self.mysql.connection.cursor()
                cur.execute('INSERT INTO inventario (nombre_inventario, fecha_creacion, notas) VALUES (%s, %s, %s)', (nombre, fecha_creacion, notas))
                self.mysql.connection.commit()
                flash('Producto agregado al inventario exitosamente.', 'success')
                return redirect(url_for('inventario'))

        @self.app.route('/edit_inventario/<int:id_inventario>')
        def edit_inventario(id_inventario):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM inventario WHERE id_inventario = %s', (id_inventario,))
            inventario = cur.fetchone()
            cur.close()
            return render_template('edit_inventario.html', inventario=inventario)

        @self.app.route('/update_inventario/<int:id_inventario>', methods=['POST'])
        def update_inventario(id_inventario):
            if request.method == 'POST':
                nombre = request.form['nombre']
                notas = request.form['notas']
                cur = self.mysql.connection.cursor()
                cur.execute("""UPDATE inventario
                            SET nombre_inventario = %s, notas = %s
                            WHERE id_inventario = %s""", (nombre, notas, id_inventario))
                self.mysql.connection.commit()
                flash('Producto actualizado en el inventario exitosamente.', 'success')
                return redirect(url_for('inventario'))

        @self.app.route('/agregar_producto/<int:id_inventario>')
        def agregar_producto(id_inventario):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM inventario_producto WHERE id_inventario = %s', (id_inventario,))
            data = cur.fetchall()
            cur.execute("SELECT * FROM producto")
            producto = cur.fetchall()
            return render_template('inventario.html', producto_inventario=data, producto=producto)

        @self.app.route('/agregar_producto_inventario/<int:id_inventario>', methods=['POST'])
        def agregar_producto_inventario(id_inventario):
            if request.method == 'POST':
                referencia = request.form['referencia']
                cur = self.mysql.connection.cursor()
                try:
                    cur.execute("""INSERT INTO inventario_producto (id_inventario, referencia) VALUES (%s, %s)""", (id_inventario, referencia))
                    self.mysql.connection.commit()
                    flash('Producto agregado al inventario exitosamente.', 'success')
                except Exception as e:
                    self.mysql.connection.rollback()
                    flash(f'Error al agregar producto al inventario: {str(e)}', 'danger')
                finally:
                    return redirect(url_for('inventario'))

        @self.app.route('/consultar_producto_inventario/<int:id_inventario>', methods=['GET'])
        def consultar_producto_inventario(id_inventario):
            cur = self.mysql.connection.cursor()
            cur.execute("""SELECT ip.id_inventario, 
                            i.nombre_inventario, 
                            p.nombre, 
                            p.cantidad
                        FROM inventario_producto ip
                        JOIN producto p ON ip.referencia = p.referencia
                        JOIN inventario i ON ip.id_inventario = i.id_inventario
                        WHERE ip.id_inventario = %s""", (id_inventario,))
            inventario_producto = cur.fetchall()
            return render_template('inventario.html', inventario_producto=inventario_producto)
