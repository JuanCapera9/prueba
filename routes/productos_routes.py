from flask import render_template, request, redirect, url_for, flash

class ProductosRoutes:
    def __init__(self, app, mysql):
        self.app = app
        self.mysql = mysql
        self.add_routes()

    def add_routes(self):
        @self.app.route('/productos')
        def productos():
            cur = self.mysql.connection.cursor()
            cur.execute("""SELECT prod.referencia, 
                            prod.nombre,
                            prod.descripcion, 
                            prod.cantidad, 
                            prod.precio,  
                            prod.medida_l, 
                            prod.medida_a,
                            prod.tipomedida, 
                            cat.nombre AS Categoria, 
                            p.nombre AS Proveedor
                        FROM producto prod
                        JOIN proveedores p ON prod.proveedor = p.id_proveedor 
                        JOIN categorias cat ON prod.categoria = cat.id_categoria""")
            data = cur.fetchall()
            cur.execute('SELECT id_categoria, nombre FROM categorias')
            categorias = cur.fetchall()
            cur.execute('SELECT id_proveedor, nombre FROM proveedores')
            proveedores = cur.fetchall()
            return render_template('productos.html', productos=data, categorias=categorias, proveedores=proveedores)

        @self.app.route('/add_productos', methods=['GET', 'POST'])
        def add_productos():
            if request.method == "POST":
                referencia = request.form['referencia']
                nombre = request.form['nombre']
                descripcion = request.form['descripcion']
                cantidad = request.form['cantidad']
                precio = request.form['precio']
                medida_l = request.form['medida_l']
                medida_a = request.form['medida_a']
                tipomedida = request.form['tipomedida']
                categoria_id = request.form['categoria']
                proveedor_id = request.form['proveedor']

                cur = self.mysql.connection.cursor()
                cur.execute('INSERT INTO producto (referencia, nombre, descripcion, cantidad, precio, medida_l, medida_a, tipomedida, categoria, proveedor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (referencia, nombre, descripcion, cantidad, precio, medida_l, medida_a, tipomedida, categoria_id, proveedor_id))
                self.mysql.connection.commit()
                flash('Producto agregado exitosamente.', 'success')
                return redirect(url_for('productos'))
            else:
                cur = self.mysql.connection.cursor()
                cur.execute('SELECT * FROM categorias')
                categorias = cur.fetchall()
                cur.execute('SELECT * FROM proveedores')
                proveedores = cur.fetchall()
                return render_template('producto.html', categorias=categorias, proveedores=proveedores)

        @self.app.route('/edit/<referencia>')
        def get_producto(referencia):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM producto WHERE referencia = %s', (referencia,))
            data = cur.fetchone()
            return render_template('edit_producto.html', producto=data)

        @self.app.route('/update/<referencia>', methods=['POST'])
        def update_producto(referencia):
            if request.method == 'POST':
                nombre = request.form['nombre']
                descripcion = request.form['descripcion']
                precio = request.form['precio']
                medida_l = request.form['medida_l']
                medida_a = request.form['medida_a']
                tipomedida = request.form['tipomedida']
                categoria_id = request.form['categoria']
                proveedor_id = request.form['proveedor']

                cur = self.mysql.connection.cursor()
                cur.execute(
                    'UPDATE producto SET nombre = %s, descripcion = %s, precio = %s, medida_l = %s, medida_a = %s, tipomedida = %s, categoria = %s, proveedor = %s WHERE referencia = %s',
                    (nombre, descripcion, precio, medida_l, medida_a, tipomedida, categoria_id, proveedor_id, referencia))
                self.mysql.connection.commit()
                flash('Producto actualizado exitosamente.', 'success')
            return redirect(url_for('productos'))
