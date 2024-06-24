from flask import render_template, request, redirect, url_for, flash
from datetime import datetime

class UsuariosRoutes:
    def __init__(self, app, mysql):
        self.app = app
        self.mysql = mysql
        self.add_routes()

    def add_routes(self):
        @self.app.route('/usuarios')
        def usuarios():
            cur = self.mysql.connection.cursor()
            cur.execute("""SELECT usu.id_usuario, 
                            usu.correo, 
                            usu.nombre_usuario, 
                            usu.fecha_registro, 
                            esu.tipo_estado AS Estado,
                            COALESCE(rol.nombre_rol, 'Sin Rol') AS Rol,
                            usu.id_estado_usuario,
                            usu.id_rol
                        FROM usuarios usu
                        JOIN estado_usuarios esu ON usu.id_estado_usuario = esu.id_estado_usuario
                        LEFT JOIN roles rol ON usu.id_rol = rol.id_rol""")
            data = cur.fetchall()

            cur.execute('SELECT id_estado_usuario, tipo_estado FROM estado_usuarios')
            estado_usuarios = cur.fetchall()

            cur.execute('SELECT id_rol, nombre_rol FROM roles')
            roles = cur.fetchall()

            return render_template('usuarios.html', usuarios=data, estado_usuarios=estado_usuarios, roles=roles)

        @self.app.route('/add_usuario', methods=['POST'])
        def add_usuario():
            if request.method == 'POST':
                correo = request.form['correo']
                nombre_usuario = request.form['nombre_usuario']
                id_estado_usuario = request.form.get('estado', 1) 
                id_rol = request.form['id_rol']

                fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                cur = self.mysql.connection.cursor()
                cur.execute('INSERT INTO usuarios (correo, nombre_usuario, fecha_registro, id_estado_usuario, id_rol) VALUES (%s, %s, %s, %s, %s, %s)', 
                            (correo, nombre_usuario, fecha_registro, id_estado_usuario, id_rol))
                self.mysql.connection.commit()
                flash('Usuario agregado exitosamente.', 'success')
                return redirect(url_for('usuarios'))

        @self.app.route('/edit_usuario/<int:id_usuario>')
        def edit_usuario(id_usuario):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM usuarios WHERE id_usuario = %s', (id_usuario,))
            data = cur.fetchone()

            cur.execute('SELECT id_estado_usuario, tipo_estado FROM estado_usuarios')
            estado_usuarios = cur.fetchall()

            cur.execute('SELECT id_rol, nombre_rol FROM roles')
            roles = cur.fetchall()

            return render_template('edit_usuario.html', usuario=data, estado_usuarios=estado_usuarios, roles=roles)

        @self.app.route('/update_usuario/<int:id_usuario>', methods=['POST'])
        def update_usuario(id_usuario):
            if request.method == 'POST':
                correo = request.form['correo']
                nombre_usuario = request.form['nombre_usuario']
                id_estado_usuario = request.form['id_estado_usuario']
                id_rol = request.form['id_rol']

                cur = self.mysql.connection.cursor()
                cur.execute("""
                    UPDATE usuarios
                    SET correo = %s,
                        nombre_usuario = %s,
                        id_estado_usuario = %s,
                        id_rol = %s
                    WHERE id_usuario = %s
                """, (correo, nombre_usuario, id_estado_usuario, id_rol, id_usuario))
                self.mysql.connection.commit()
                flash('Usuario actualizado exitosamente.', 'success')
                return redirect(url_for('usuarios'))
