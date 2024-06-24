from flask import render_template, request, redirect, url_for, flash
from datetime import datetime

class MovimientosRoutes:
    def __init__(self, app, mysql):
        self.app = app
        self.mysql = mysql
        self.add_routes()
    
    def add_routes(self):
        @self.app.route('/movimientos')
        def movimientos():
            try:
                cur = self.mysql.connection.cursor()
                
                # Consultar entradas y salidas de inventario
                cur.execute("""SELECT * FROM entrada_inventario""")
                entrada_inventario = cur.fetchall()
                
                cur.execute("""
                    SELECT s.id_salida_inventario, s.Cantidad, s.fecha_salida, s.Motivo, e.nombres, e.apellidos
                    FROM salidas_inventario s
                    JOIN empleados e ON s.empleado = e.id_empleado
                """)
                salidas_inventario = cur.fetchall()
                
                # Consultar productos y empleados
                cur.execute("""SELECT * FROM producto""")
                productos = cur.fetchall()
                cur.execute("""SELECT * FROM empleados""")
                empleados = cur.fetchall()

                cur.close()

                return render_template('movimientos.html', entrada_inventario=entrada_inventario, 
                                       salidas_inventario=salidas_inventario, productos=productos, 
                                       empleados=empleados)
            except Exception as e:
                flash(f'Error al cargar los movimientos: {str(e)}', 'danger')
                return redirect(url_for('index'))
        
        @self.app.route('/crear_entrada', methods=['POST'])
        def crear_entrada():
            if request.method == 'POST':
                cantidad_entrada = int(request.form['cantidad_entrada'])
                referencia = request.form['referencia']

                # Validación básica de datos
                if not cantidad_entrada or not referencia:
                    flash('Todos los campos son requeridos.', 'warning')
                    return redirect(url_for('movimientos'))

                try:
                    fecha_entrada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    cur = self.mysql.connection.cursor()

                    # Insertar entrada en inventario
                    cur.execute("""
                        INSERT INTO entrada_inventario (cantidad_entrada, fecha_entrada, referencia)
                        VALUES (%s, %s, %s)
                    """, (cantidad_entrada, fecha_entrada, referencia))
                    
                    # Actualizar cantidad en tabla producto
                    cur.execute("""
                        UPDATE producto
                        SET cantidad = cantidad + %s
                        WHERE referencia = %s
                    """, (cantidad_entrada, referencia))

                    self.mysql.connection.commit()
                    flash('Entrada en inventario creada correctamente.', 'success')
                except Exception as e:
                    flash(f'Error al crear la entrada en inventario: {str(e)}', 'danger')
                
                return redirect(url_for('movimientos'))
        
        @self.app.route('/crear_salida', methods=['POST'])
        def crear_salida():
            if request.method == 'POST':
                cantidad_salida = int(request.form['cantidad_salida'])
                motivo = request.form['motivo']
                id_empleado = int(request.form['id_empleado'])
                referencia = request.form['referencia']

                # Validación básica de datos
                if not cantidad_salida or not motivo or not id_empleado or not referencia:
                    flash('Todos los campos son requeridos.', 'warning')
                    return redirect(url_for('movimientos'))

                try:
                    fecha_salida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    cur = self.mysql.connection.cursor()

                    # Insertar salida en inventario
                    cur.execute("""
                        INSERT INTO salidas_inventario (Cantidad, fecha_salida, Motivo, empleado, referencia)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (cantidad_salida, fecha_salida, motivo, id_empleado, referencia))
                    
                    # Actualizar cantidad en tabla producto
                    cur.execute("""
                        UPDATE producto
                        SET cantidad = cantidad - %s
                        WHERE referencia = %s
                    """, (cantidad_salida, referencia))

                    self.mysql.connection.commit()
                    flash('Salida en inventario creada correctamente.', 'success')
                except Exception as e:
                    flash(f'Error al crear la salida en inventario: {str(e)}', 'danger')
                
                return redirect(url_for('movimientos'))
        
        @self.app.route('/consultar_entradas/<referencia>', methods=['GET'])
        def consultar_entradas(referencia):
            try:
                cur = self.mysql.connection.cursor()
                cur.execute("""
                    SELECT fecha_entrada, cantidad_entrada
                    FROM entrada_inventario
                    WHERE referencia = %s
                """, (referencia,))
                entradas = cur.fetchall()
                cur.close()

                return render_template('movimientos.html', entradas=entradas)
            except Exception as e:
                flash(f'Error al consultar las entradas: {str(e)}', 'danger')
                return redirect(url_for('movimientos'))
            
        @self.app.route('/consultar_salidas/<referencia>', methods=['GET'])
        def consultar_salidas(referencia):
            try:
                cur = self.mysql.connection.cursor()
                cur.execute("""
                    SELECT s.id_salida_inventario, s.Cantidad, s.fecha_salida, s.Motivo, e.nombres, e.apellidos
                    FROM salidas_inventario s
                    JOIN empleados e ON s.empleado = e.id_empleado
                    WHERE s.referencia = %s
                """, (referencia,))
                salidas = cur.fetchall()
                cur.close()

                return render_template('movimientos.html', salidas=salidas)
            except Exception as e:
                flash(f'Error al consultar las salidas: {str(e)}', 'danger')
                return redirect(url_for('movimientos'))
