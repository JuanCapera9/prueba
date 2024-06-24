from flask import render_template, request, redirect, url_for, flash

class ClientesRoutes:
    def __init__(self, app, mysql):
        self.app = app
        self.mysql = mysql
        self.add_routes()

    def add_routes(self):
        @self.app.route('/clientes')
        def clientes():
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM clientes')
            data = cur.fetchall()
            return render_template('clientes.html', clientes=data)

        @self.app.route('/add_cliente', methods=['POST'])
        def add_cliente():
            if request.method == 'POST':
                nombres = request.form['nombres']
                apellidos = request.form['apellidos']
                documento = request.form['documento']
                email = request.form['email']
                direccion = request.form['direccion']
                telefono = request.form['telefono']
                cur = self.mysql.connection.cursor()
                cur.execute('INSERT INTO clientes (nombres, apellidos, documento, email, direccion, telefono) VALUES (%s, %s, %s, %s, %s, %s)', 
                            (nombres, apellidos, documento, email, direccion, telefono))
                self.mysql.connection.commit()
                flash('Cliente agregado exitosamente.', 'success')
                return redirect(url_for('clientes'))

        @self.app.route('/edit_cliente/<id_cliente>')
        def get_cliente(id_cliente):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM clientes WHERE id_cliente = %s', (id_cliente,))
            data = cur.fetchone()
            return render_template('edit_cliente.html', cliente=data)

        @self.app.route('/update_cliente/<id_cliente>', methods=['POST'])
        def update_cliente(id_cliente):
            if request.method == 'POST':
                nombres = request.form['nombres']
                apellidos = request.form['apellidos']
                documento = request.form['documento']
                email = request.form['email']
                direccion = request.form['direccion']
                telefono = request.form['telefono']
                cur = self.mysql.connection.cursor()
                cur.execute('UPDATE clientes SET nombres = %s, apellidos = %s, documento = %s, email = %s, direccion = %s, telefono = %s WHERE id_cliente = %s',
                            (nombres, apellidos, documento, email, direccion, telefono, id_cliente))
                self.mysql.connection.commit()
                flash('Cliente actualizado exitosamente.', 'success')
                return redirect(url_for('clientes'))
