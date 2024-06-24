from flask import render_template, request, redirect, url_for, flash

class EmpleadosRoutes:
    def __init__(self, app, mysql):
        self.app = app
        self.mysql = mysql
        self.add_routes()

    def add_routes(self):
        @self.app.route('/empleados')
        def empleados():
            cur = self.mysql.connection.cursor()
            cur.execute("""SELECT emp.id_Empleado,
                            emp.nombres,
                            emp.apellidos,
                            emp.documento,
                            emp.email,
                            emp.telefono,
                            car.nombre_cargo AS Cargo,
                            car.id_cargo
                        FROM empleados emp
                        JOIN cargos car ON emp.cargo = car.id_cargo""")
            data = cur.fetchall()
            cur.execute('SELECT id_cargo, nombre_cargo FROM cargos')
            cargos = cur.fetchall()
            return render_template('empleados.html', empleados = data, cargos = cargos)

        @self.app.route('/add_empleado', methods=['POST'])
        def add_empleado():
            if request.method == 'POST':
                nombres = request.form['nombres']
                apellidos = request.form['apellidos']
                documento = request.form['documento']
                email = request.form['email']
                telefono = request.form['telefono']
                cargo = request.form['cargo']

                cur = self.mysql.connection.cursor()
                cur.execute('INSERT INTO empleados (nombres, apellidos, documento, email, telefono, cargo) VALUES (%s, %s, %s, %s, %s, %s)', (nombres, apellidos, documento, email, telefono, cargo))
                self.mysql.connection.commit()
                flash('Empleado agregado exitosamente.', 'success')
            return redirect(url_for('empleados'))

        @self.app.route('/edit_empleado/<id_empleado>')
        def get_empleado(id_empleado):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM empleados WHERE id_empleado = %s', (id_empleado,))
            data = cur.fetchone()
            return render_template('edit_empleado.html', empleado=data)

        @self.app.route('/update_empleado/<id_empleado>', methods=['POST'])
        def update_empleado(id_empleado):
            if request.method == 'POST':
                nombres = request.form['nombres']
                apellidos = request.form['apellidos']
                documento = request.form['documento']
                email = request.form['email']
                telefono = request.form['telefono']
                cargo = request.form['cargo']

                cur = self.mysql.connection.cursor()
                cur.execute("""
                    UPDATE empleados
                    SET nombres = %s,
                        apellidos = %s,
                        documento = %s,
                        email = %s,
                        telefono = %s,
                        cargo = %s
                    WHERE id_empleado = %s
                """, (nombres, apellidos, documento, email, telefono, cargo, id_empleado))
                self.mysql.connection.commit()
                flash('Empleado actualizado exitosamente.', 'success')
            return redirect(url_for('empleados'))
