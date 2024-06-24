from flask import render_template, request, redirect, url_for, flash
from datetime import datetime

class VentasRoutes:
    def __init__(self, app, mysql):
        self.app = app
        self.mysql = mysql
        self.add_routes()
    
    def add_routes(self):
        @self.app.route('/ventas')
        def ventas():
            cur = self.mysql.connection.cursor()
            cur.execute("""SELECT ven.id_venta,
                            ven.fecha_venta,
                            ven.total,
                            CONCAT(cli.nombres, ' ', cli.apellidos) AS nombrecliente,
                            cli.id_cliente
                        FROM ventas ven
                        INNER JOIN clientes cli ON ven.id_cliente = cli.id_cliente""")
            data = cur.fetchall()
            cur.execute('SELECT id_cliente, CONCAT(nombres, " ", apellidos) AS nombre_cliente FROM clientes')
            cliente = cur.fetchall()
            cur.execute("SELECT * FROM producto")
            producto = cur.fetchall()
            cur.execute("""SELECT dv.id_venta,
                            CONCAT(c.nombres, ' ', c.apellidos) AS nombre_cliente,
                            v.fecha_venta,
                            p.nombre AS nombre_producto,
                            SUM(dv.cantidad_vendida) AS cantidad_total_vendida,
                            p.precio AS precio_producto,
                            SUM(dv.cantidad_vendida * p.precio) AS subtotal,
                            v.total AS precio_venta
                        FROM detalles_ventas dv
                        JOIN producto p ON dv.referencia = p.referencia
                        JOIN ventas v ON dv.id_venta = v.id_venta
                        JOIN clientes c ON v.id_cliente = c.id_cliente
                        GROUP BY dv.id_venta, nombre_cliente, v.fecha_venta, p.nombre, p.precio, v.total""")
            detalles_ventas = cur.fetchall()

            return render_template('ventas.html', ventas=data, cliente=cliente, producto=producto, detalles_ventas=detalles_ventas)

        @self.app.route('/add_venta', methods=['POST'])
        def add_venta():
            if request.method == 'POST':
                id_cliente = request.form['id_cliente']
                fecha_venta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                total = 0

                cur = self.mysql.connection.cursor()
                cur.execute('INSERT INTO ventas (id_cliente, fecha_venta, total) VALUES (%s, %s, %s)', 
                            (id_cliente, fecha_venta, total))
                self.mysql.connection.commit()
                flash('Venta agregada exitosamente.', 'success')
                return redirect(url_for('ventas'))

        @self.app.route('/edit_venta/<int:id_venta>')
        def edit_venta(id_venta):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM ventas WHERE id_venta = %s', (id_venta,))
            data = cur.fetchone()

            cur.execute("SELECT CONCAT(nombres, ' ', apellidos) AS nombre_cliente FROM clientes")
            cliente = cur.fetchall()
            return render_template('ventas.html', venta=data, cliente=cliente)

        @self.app.route('/update_venta/<int:id_venta>', methods=['POST'])
        def update_venta(id_venta):
            if request.method == 'POST':
                id_cliente = request.form['id_cliente']

                cur = self.mysql.connection.cursor()
                cur.execute("""UPDATE ventas
                    SET id_cliente = %s
                    WHERE id_venta = %s""", (id_cliente, id_venta))
                self.mysql.connection.commit()
                flash('Venta actualizada exitosamente.', 'success')
                return redirect(url_for('ventas'))
            
        @self.app.route('/agregar_venta/<int:id_venta>')
        def agregar_venta(id_venta):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM detalles_ventas WHERE id_venta = %s', (id_venta,))
            data = cur.fetchall()  # Usamos fetchall en lugar de fetchone para obtener todos los detalles
            cur.execute("SELECT * FROM producto")
            producto = cur.fetchall()
            return render_template('ventas.html', detalles_ventas=data, producto=producto)
        
        @self.app.route('/agregar_venta_producto/<int:id_venta>', methods=['POST'])
        def agregar_venta_producto(id_venta):
            if request.method == 'POST':
                referencia = request.form['referencia']
                cantidad_vendida = int(request.form['cantidad_vendida'])

                cur = self.mysql.connection.cursor()
                cur.execute('SELECT cantidad FROM producto WHERE referencia = %s', (referencia,))
                cantidad_producto = cur.fetchone()[0]

                if cantidad_producto >= cantidad_vendida:
                    nueva_cantidad_producto = cantidad_producto - cantidad_vendida
                    cur.execute('UPDATE producto SET cantidad = %s WHERE referencia = %s', (nueva_cantidad_producto, referencia))
                    self.mysql.connection.commit()

                    cur.execute("""INSERT INTO detalles_ventas (cantidad_vendida, referencia, id_venta) VALUES (%s, %s, %s)""", 
                                (cantidad_vendida, referencia, id_venta))
                    self.mysql.connection.commit()
                    
                    cur.execute('SELECT precio FROM producto WHERE referencia = %s', (referencia,))
                    precio_producto = cur.fetchone()[0]
                    
                    total_producto = precio_producto * cantidad_vendida

                    cur.execute('SELECT total FROM ventas WHERE id_venta = %s', (id_venta,))
                    total_venta = cur.fetchone()[0]

                    nuevo_total_venta = total_venta + total_producto

                    cur.execute("""UPDATE ventas
                                    SET total = %s
                                    WHERE id_venta = %s""", (nuevo_total_venta, id_venta))
                    self.mysql.connection.commit()

                    flash('Producto agregado exitosamente.', 'success')
                    return redirect(url_for('ventas'))
                else:
                    flash('No hay suficientes productos en stock.', 'error')
                    return redirect(url_for('ventas'))
                
        @self.app.route('/consultar_detalle/<int:id_venta>', methods=['GET'])
        def consultar_detalle(id_venta):
            cur = self.mysql.connection.cursor()
            cur.execute("""SELECT dv.id_venta,
                            CONCAT(c.nombres, ' ', c.apellidos) AS nombre_cliente,
                            v.fecha_venta,
                            p.nombre AS nombre_producto,
                            SUM(dv.cantidad_vendida) AS cantidad_total_vendida,
                            p.precio AS precio_producto,
                            SUM(dv.cantidad_vendida * p.precio) AS subtotal,
                            v.total AS precio_venta
                        FROM detalles_ventas dv
                        JOIN producto p ON dv.referencia = p.referencia
                        JOIN ventas v ON dv.id_venta = v.id_venta
                        JOIN clientes c ON v.id_cliente = c.id_cliente
                        WHERE dv.id_venta = %s
                        GROUP BY dv.id_venta, nombre_cliente, v.fecha_venta, p.nombre, p.precio, v.total""", (id_venta,))
            detalles_ventas = cur.fetchall()

            return render_template('ventas.html', detalles_ventas=detalles_ventas)
        
        @self.app.route('/salidas_inventario')
        def salidas_inventario():
            cur = self.mysql.connection.cursor()
            cur.execute("""
                SELECT s.id_salida_inventario, s.Cantidad, s.fecha_salida, s.Motivo, s.empleado, e.nombres, e.apellidos
                FROM salidas_inventario s
                JOIN empleados e ON s.empleado = e.id_empleado
            """)
            data = cur.fetchall()
            return render_template('salidas_inventario.html', salidas_inventario=data)

        @self.app.route('/indexVentas')
        def indexVentas():
            return render_template('ventas.html')
