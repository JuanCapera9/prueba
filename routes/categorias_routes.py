from flask import render_template, request, redirect, url_for, flash

class CategoriasRoutes:
    def __init__(self, app, mysql):
        self.app = app
        self.mysql = mysql
        self.register_routes()

    def register_routes(self):
        @self.app.route('/categorias')
        def categorias():
            cur = self.mysql.connection.cursor()
            # Obtener todas las categorías existentes
            cur.execute('SELECT * FROM categorias')
            data = cur.fetchall()
            cur.close()

            return render_template('categorias.html', data=data)

        @self.app.route('/add_categoria', methods=['POST'])
        def add_categoria():
                if request.method == 'POST':
                    descripcion = request.form['descripcion']
                    nombre = request.form['nombre']
                    

                    cur = self.mysql.connection.cursor()
                    cur.execute('INSERT INTO categorias (descripcion, nombre) VALUES (%s, %s)',
                                (descripcion, nombre))
                    self.mysql.connection.commit()

                    flash('Categoria agregada exitosamente.', 'success')
                return redirect(url_for('categorias'))
        
        @self.app.route('/edit_categoria/<id_categoria>')
        def get_categoria(id_categoria):
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT * FROM categorias WHERE id_categoria = %s', (id_categoria))
            data = cur.fetchone()

            return render_template('edit_categoria.html', categoria = data)

        @self.app.route('/update_categoria/<id_categoria>', methods=['POST'])
        def update_categoria(id_categoria):
            if request.method == 'POST':
                descripcion = request.form['descripcion']
                nombre = request.form['nombre']
                cur = self.mysql.connection.cursor()
                cur.execute('UPDATE categorias SET descripcion = %s, nombre = %s WHERE id_categoria = %s',
                                (descripcion, nombre, id_categoria))
                self.mysql.connection.commit()

                flash('Categoría actualizada exitosamente.', 'success')
            return redirect(url_for('categorias'))
