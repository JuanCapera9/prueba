from flask import render_template, request, redirect, url_for, flash

class ProveedoresRoutes:
    def __init__(self, app, mysql):
        self.app = app
        self.mysql = mysql
        self.add_routes()

    def add_routes(self):
        @self.app.route('/proveedores')
        def proveedores():
            cur = self.mysql.connection.cursor()
            cur.execute("""
                SELECT prov.id_proveedor,
                       prov.nombre,
                       prov.apellido,
                       prov.email,
                       prov.telefono,
                       prov.ciudad,
                       prov.direccion,
                       esu.tipo_estado AS Estado
                FROM proveedores prov
                JOIN estado_usuarios esu ON prov.estado = esu.id_estado_usuario;
            """)
            data = cur.fetchall()

            cur.execute('SELECT id_estado_usuario, tipo_estado FROM estado_usuarios')
            estado_usuarios = cur.fetchall()
            
            return render_template('proveedores.html', proveedores=data, estado_usuarios = estado_usuarios)

        @self.app.route('/add_proveedor', methods=['POST'])
        def add_proveedor():
            if request.method == 'POST':
                apellido = request.form['apellido']
                ciudad = request.form['ciudad']
                direccion = request.form['direccion']
                email = request.form['email']
                nombre = request.form['nombre']
                telefono = request.form['telefono']
                estado = request.form.get('estado', 1) 

                cur = self.mysql.connection.cursor()
                cur.execute('INSERT INTO proveedores (nombre, apellido, email, telefono, ciudad, direccion, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                            (nombre, apellido, email, telefono, ciudad, direccion, estado))
                self.mysql.connection.commit()

                flash('Proveedor agregado exitosamente.', 'success')
            return redirect(url_for('proveedores'))

        @self.app.route('/edit_proveedor/<id_proveedor>')
        def get_proveedor(id_proveedor):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM proveedores WHERE id_proveedor = %s', (id_proveedor))
            data = cur.fetchone()

            cur.execute('SELECT id_estado_usuario, tipo_estado FROM estado_usuarios')
            estado_usuarios = cur.fetchall()

            return render_template('edit_proveedor.html', proveedor=data, estado_usuarios = estado_usuarios)

        @self.app.route('/update_proveedor/<id_proveedor>', methods=['POST'])
        def update_proveedor(id_proveedor):
            if request.method == 'POST':
                apellido = request.form['apellido']
                ciudad = request.form['ciudad']
                direccion = request.form['direccion']
                email = request.form['email']
                nombre = request.form['nombre']
                telefono = request.form['telefono']
                estado = request.form['estado']  # Asegúrate de que el nombre del campo sea 'estado'

                cur = self.mysql.connection.cursor()
                cur.execute("""
                    UPDATE proveedores
                    SET apellido = %s,
                        ciudad = %s,
                        direccion = %s,
                        email = %s,
                        nombre = %s,
                        telefono = %s,
                        estado = %s
                    WHERE id_proveedor = %s
                """, (apellido, ciudad, direccion, email, nombre, telefono, estado, id_proveedor))
                self.mysql.connection.commit()

                flash('Proveedor actualizado exitosamente.', 'success')
            return redirect(url_for('proveedores'))
