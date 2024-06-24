from flask import render_template, request, redirect, url_for, flash
from datetime import datetime

class ComprasRoutes:
    def __init__(self, app, mysql):
        self.app = app
        self.mysql = mysql
        self.add_routes()
    
    def add_routes(self):
        @self.app.route('/compras')
        def compras():
            cur = self.mysql.connection.cursor()
            cur.execute("""SELECT com.id_compra,
                            com.fecha_compra,
                            com.total_compra,
                            CONCAT(prov.nombre, ' ', prov.apellido) AS nombreproveedor,
                            prov.id_proveedor
                        FROM compras com
                        INNER JOIN proveedores prov ON com.proveedor = prov.id_proveedor""")
            data = cur.fetchall()
            cur.execute('SELECT id_proveedor, CONCAT(nombre, " ", apellido) AS nombre_proveedor FROM proveedores')
            proveedor = cur.fetchall()
            cur.execute("SELECT * FROM producto")
            producto = cur.fetchall()
            cur.execute("""SELECT dc.id_compra,
                            CONCAT(prov.nombre, ' ', prov.apellido) AS nombre_proveedor,
                            comp.fecha_compra,
                            p.nombre AS nombre_producto,
                            SUM(dc.cantidad_compra) AS cantidad_total_vendida,
                            p.precio AS precio_producto,
                            SUM(dc.cantidad_compra * p.precio) AS subtotal,
                            comp.total_compra AS total_compra
                        FROM detalles_compras dc
                        JOIN producto p ON dc.referencia = p.referencia
                        JOIN compras comp ON dc.id_compra = comp.id_compra
                        JOIN proveedores prov ON comp.proveedor = prov.id_proveedor
                        GROUP BY dc.id_compra, nombre_proveedor, comp.fecha_compra, p.nombre, p.precio, comp.total_compra""")
            detalles_compras = cur.fetchall()

            return render_template('compras.html', compras = data, proveedor = proveedor, producto=producto, detalles_compras = detalles_compras)

        @self.app.route('/add_compra', methods=['POST'])
        def add_compra():
            if request.method == 'POST':
                proveedor = request.form['id_proveedor']
                fecha_compra = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                total_compra = 0

                cur = self.mysql.connection.cursor()
                cur.execute('INSERT INTO compras (proveedor, fecha_compra, total_compra) VALUES (%s, %s, %s)', 
                            (proveedor, fecha_compra, total_compra))
                self.mysql.connection.commit()
                flash('Compra agregada exitosamente.', 'success')
                return redirect(url_for('compras'))

        @self.app.route('/edit_compra/<int:id_compra>')
        def edit_compra(id_compra):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM compras WHERE id_compra = %s', (id_compra,))
            data = cur.fetchone()

            cur.execute("SELECT CONCAT(nombre, ' ', apellido) AS nombre_proveedor FROM proveedores")
            proveedor = cur.fetchall()
            return render_template('compras.html', compra = data, proveedor=proveedor)

        @self.app.route('/update_compra/<int:id_compra>', methods=['POST'])
        def update_compra(id_compra):
            if request.method == 'POST':
                proveedor = request.form['id_proveedor']

                cur = self.mysql.connection.cursor()
                cur.execute("""UPDATE compras
                    SET proveedor = %s
                    WHERE id_compra = %s""", (proveedor, id_compra))
                self.mysql.connection.commit()
                flash('Compra actualizada exitosamente.', 'success')
                return redirect(url_for('compras'))
            
        @self.app.route('/agregar_compra/<int:id_compra>')
        def agregar_compra(id_compra):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM detalles_compras WHERE id_compra = %s', (id_compra,))
            data = cur.fetchall()  # Usamos fetchall en lugar de fetchone para obtener todos los detalles
            cur.execute("SELECT * FROM producto")
            producto = cur.fetchall()
            return render_template('compras.html', detalles_compras=data, producto=producto)
        
        @self.app.route('/agregar_compra_producto/<int:id_compra>', methods=['POST'])
        def agregar_compra_producto(id_compra):
            if request.method == 'POST':
                referencia = request.form['referencia']
                cantidad_compra = int(request.form['cantidad_compra'])

                cur = self.mysql.connection.cursor()
                cur.execute('SELECT cantidad FROM producto WHERE referencia = %s', (referencia,))
                cantidad_producto = cur.fetchone()[0]

                if cantidad_producto >= cantidad_compra:
                    nueva_cantidad_producto = cantidad_producto + cantidad_compra
                    cur.execute('UPDATE producto SET cantidad = %s WHERE referencia = %s', (nueva_cantidad_producto, referencia))
                    self.mysql.connection.commit()

                    cur.execute("""INSERT INTO detalles_compras (cantidad_compra, referencia, id_compra) VALUES (%s, %s, %s)""", 
                                (cantidad_compra, referencia, id_compra))
                    self.mysql.connection.commit()
                    
                    cur.execute('SELECT precio FROM producto WHERE referencia = %s', (referencia,))
                    precio_producto = cur.fetchone()[0]
                    
                    total_producto = precio_producto * cantidad_compra

                    cur.execute('SELECT total_compra FROM compras WHERE id_compra = %s', (id_compra,))
                    total_compra = cur.fetchone()[0]

                    nuevo_total_compra = total_compra + total_producto

                    cur.execute("""UPDATE compras
                                    SET total_compra = %s
                                    WHERE id_compra = %s""", (nuevo_total_compra, id_compra))
                    self.mysql.connection.commit()

                    flash('Producto agregado exitosamente.', 'success')
                    return redirect(url_for('compras'))
                else:
                    flash('No hay suficientes productos en stock.', 'error')
                    return redirect(url_for('compras'))
                
        @self.app.route('/consultar_detalleCompra/<int:id_compra>', methods=['GET'])
        def consultar_detalleCompra(id_compra):
            cur = self.mysql.connection.cursor()
            cur.execute("""SELECT dc.id_compra,
                            CONCAT(prov.nombre, ' ', prov.apellido) AS nombre_proveedor,
                            com.fecha_compra,
                            p.nombre AS nombre_producto,
                            SUM(dc.cantidad_compra) AS cantidad_total_compra,
                            p.precio AS precio_producto,
                            SUM(dc.cantidad_compra * p.precio) AS subtotal,
                            com.total_compra AS precio_compra
                        FROM detalles_compras dc
                        JOIN producto p ON dc.referencia = p.referencia
                        JOIN compras com ON dc.id_compra = com.id_compra
                        JOIN proveedores prov ON com.proveedor = prov.id_proveedor
                        WHERE dc.id_compra = %s
                        GROUP BY dc.id_compra, nombre_proveedor, com.fecha_compra, p.nombre, p.precio, com.total_compra""", (id_compra,))
            detalles_compras = cur.fetchall()

            return render_template('compras.html', detalles_compras=detalles_compras)

        @self.app.route('/indexcompras')
        def indexcompras():
            return render_template('compras.html')
