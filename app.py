import logging
import re
from email.message import EmailMessage
import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import MySQLdb.cursors
import pymysql.cursors
from flask_mail import Mail, Message
import logging
# Configuración de la aplicación Flask
app = Flask(__name__)
app.config.from_object('config.Config')
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.secret_key = 'secret'

# Configuración de la base de datos MySQL
mysql = MySQL(app)

# Configuración de Flask-Bcrypt para hashing de contraseñas
bcrypt = Bcrypt(app)

# Logger
logger = logging.getLogger(__name__)

# Define las rutas permitidas para cada rol (importar según sea necesario)
from routes import CategoriasRoutes, ComprasRoutes, ClientesRoutes, ProveedoresRoutes, EmpleadosRoutes, InventarioRoutes, VentasRoutes, UsuariosRoutes, ProductosRoutes, MovimientosRoutes

# Registro de las rutas
categorias_routes = CategoriasRoutes(app, mysql)
compras_routes = ComprasRoutes(app, mysql)
clientes_routes = ClientesRoutes(app, mysql)
proveedores_routes = ProveedoresRoutes(app, mysql)
empleados_routes = EmpleadosRoutes(app, mysql)
inventario_routes = InventarioRoutes(app, mysql)
ventas_routes = VentasRoutes(app, mysql)
usuarios_routes = UsuariosRoutes(app, mysql)
productos_Routes = ProductosRoutes(app, mysql)
movimientos_Routes =  MovimientosRoutes(app, mysql)

@app.before_request
def before_request():
    g.user = None
    g.tipo_sesion = None
    g.allowed_tables = []

    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id_usuario, correo, id_rol FROM usuarios WHERE id_usuario = %s', (session['user_id'],))
        user = cur.fetchone()
        if user:
            g.user = user
            g.tipo_sesion = session['tipo_sesion']
            g.allowed_tables = get_allowed_tables(user['id_rol'])
        cur.close()

def get_allowed_tables(id_rol):
    if id_rol == 1:  # Rol 1: Todos los permisos
        return ['productos', 'categorias', 'proveedores', 'compras', 'clientes', 'ventas', 'empleados', 'usuarios', 'inventario', 'movimientos']
    elif id_rol == 2:  # Rol 2: Compras, Proveedores, Categorías, Productos
        return ['compras', 'proveedores', 'categorias', 'productos']
    elif id_rol == 3:  # Rol 3: Ventas y Clientes
        return ['ventas', 'clientes']
    elif id_rol == 4:  # Rol 4: Productos, Categorías, Inventario
        return ['productos', 'categorias', 'inventario', 'movimientos']
    else:
        return []




# Define las tablas permitidas para cada rol
role_tables = {
    1: ['productos', 'categorias', 'proveedores', 'clientes', 'empleados', 'usuarios', 'inventario', 'ventas', 'compras', 'movimientos'],
    2: ['productos', 'categorias', 'proveedores', 'compras'],
    3: ['clientes', 'ventas'],
    4: ['productos', 'categorias', 'inventario', 'movimientos']
}

# Función para generar token de restablecimiento de contraseña
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

# Función para verificar el token de restablecimiento de contraseña
def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except SignatureExpired:
        return None  # Token expirado
    except BadSignature:
        return None  # Token inválido
    return email

# Ruta para solicitar recuperación de contraseña
@app.route("/web/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        correo = request.form["correo"]
        logger.info("Correo de recuperación enviado a %s", correo)

        # Conexión a la base de datos para verificar si el correo existe
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (correo,))
        user = cursor.fetchone()

        if user:
            try:
                # Generar token de restablecimiento
                token = generate_reset_token(correo)

                # Envío del correo de recuperación con el enlace que incluye el token
                enlace_recuperacion = url_for('cambiar_contrasena', token=token, _external=True)
                
                msg = EmailMessage()
                msg.set_content(f"Haz clic en el siguiente enlace para cambiar tu contraseña: {enlace_recuperacion}")
                msg['Subject'] = "Recuperar Contraseña"
                msg['From'] = "bmp77576@gmail.com"
                msg['To'] = correo

                with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
                    servidor.starttls()
                    servidor.login("bmp77576@gmail.com", "ikcy rzsz hape ychv")
                    servidor.send_message(msg)

                flash("Correo de recuperación enviado!", "success")
            except smtplib.SMTPException as e:
                flash(f"Error al enviar correo de recuperación: {str(e)}", "error")
            except Exception as e:
                flash(f"Error inesperado al enviar correo de recuperación: {str(e)}", "error")
        else:
            flash("Correo electrónico no registrado", "error")

        cursor.close()
        return redirect(url_for('recuperar'))

    return render_template("recuperar.html")

# Ruta para cambiar la contraseña con token
@app.route("/web/cambiar_contrasena/<token>", methods=["GET", "POST"])
def cambiar_contrasena(token):
    if request.method == "GET":
        try:
            correo = verify_reset_token(token)
            if correo:
                session['reset_correo'] = correo
                return render_template("cambiar_contrasena.html", token=token)
            else:
                flash('Token de recuperación no válido o expirado', 'danger')
                return redirect(url_for('recuperar'))
        except Exception as e:
            flash('Error al procesar el token de recuperación', 'danger')
            logger.error(f"Error al procesar token de recuperación: {str(e)}")
            return redirect(url_for('recuperar'))

    if request.method == "POST":
        if 'reset_correo' not in session:
            flash('No se ha solicitado recuperación de contraseña', 'danger')
            return redirect(url_for('recuperar'))

        nueva_contrasena = request.form["nueva_contrasena"]

        if nueva_contrasena:
            # Hashear la nueva contraseña
            nueva_contrasena_hash = bcrypt.generate_password_hash(nueva_contrasena).decode('utf-8')

            # Obtener el correo del usuario desde la sesión
            correo = session['reset_correo']

            # Actualizar la contraseña en la base de datos
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("UPDATE usuarios SET contraseña = %s WHERE correo = %s",
                           (nueva_contrasena_hash, correo))
            mysql.connection.commit()
            cursor.close()

            flash("Contraseña cambiada exitosamente!", "success")
            # Limpiar la sesión después de cambiar la contraseña
            session.pop('reset_correo', None)
            return redirect(url_for('login'))  # Redirige a la página de inicio de sesión

        else:
            flash("Por favor ingresa una nueva contraseña.", "error")

        return redirect(url_for('cambiar_contrasena', token=token))

    return render_template("cambiar_contrasena.html", token=token)

# Página de inicio redirige a la página de inicio de sesión
@app.route('/')
def home():
    return redirect(url_for('login'))
# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()  # Borra todas las variables de sesión
    flash('Has cerrado sesión con éxito', 'info')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'correo' in request.form and 'contraseña' in request.form:
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            flash('Correo electrónico inválido', 'danger')
            return render_template('login.html')

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
        usuario = cursor.fetchone()

        if usuario and bcrypt.check_password_hash(usuario[3], contraseña):  # usuario[3] es la columna contraseña
            if usuario[5] != 1:  # 5 es la posición de id_estado_usuario en la tupla
                flash('Tu cuenta está inactiva. Contacta al administrador.', 'danger')
                return render_template('login.html')

            flash('Has iniciado sesión con éxito', 'success')
            session['id_usuario'] = usuario[0]  # 0 es la posición de id_usuario en la tupla
            session['role'] = usuario[6]  # 6 es la posición de id_rol en la tupla
            session['allowed_tables'] = role_tables.get(usuario[6], [])
            session['nav_role'] = usuario[6]

            # Obtener y guardar el nombre de usuario en la sesión
            session['nombre_usuario'] = usuario[2]  # 2 es la posición de nombre_usuario en la tupla

            return redirect(url_for('index'))
        
        else:
            flash('Correo o contraseña incorrectos', 'danger')

    return render_template('login.html')


# Página de registro de usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'correo' in request.form and 'contraseña' in request.form and 'nombre_usuario' in request.form:
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        nombre_usuario = request.form['nombre_usuario']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            flash('Correo electrónico inválido', 'danger')
            return render_template('login.html')

        if not validate_password(contraseña):
            flash('La contraseña debe tener entre 8 y 12 caracteres y contener al menos una letra mayúscula', 'danger')
            return render_template('login.html')

        # Verificar si el correo ya está registrado
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_usuario FROM usuarios WHERE correo = %s', (correo,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('El correo electrónico ya está registrado. Intente con otro correo.', 'danger')
            return render_template('login.html')

        id_estado_usuario = 1
        contraseña_hash = bcrypt.generate_password_hash(contraseña).decode('utf-8')

        cursor.execute('INSERT INTO usuarios (contraseña, correo, fecha_registro, nombre_usuario, id_estado_usuario) VALUES (%s, %s, NOW(), %s, %s)', 
                       (contraseña_hash, correo, nombre_usuario, id_estado_usuario))
        mysql.connection.commit()
        flash('Usuario registrado con éxito', 'success')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/registerCrud', methods=['GET', 'POST'])
def registerCrud():
    if request.method == 'POST' and 'correo' in request.form and 'contraseña' in request.form and 'nombre_usuario' in request.form:
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        nombre_usuario = request.form['nombre_usuario']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            flash('Correo electrónico inválido', 'danger')
            return render_template('usarios.html')

        if not validate_password(contraseña):
            flash('La contraseña debe tener entre 8 y 12 caracteres y contener al menos una letra mayúscula', 'danger')
            return render_template('login.html')

        # Verificar si el correo ya está registrado
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_usuario FROM usuarios WHERE correo = %s', (correo,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('El correo electrónico ya está registrado. Intente con otro correo.', 'danger')
            return render_template('usuarios.html')

        id_estado_usuario = 1
        contraseña_hash = bcrypt.generate_password_hash(contraseña).decode('utf-8')

        cursor.execute('INSERT INTO usuarios (contraseña, correo, fecha_registro, nombre_usuario, id_estado_usuario) VALUES (%s, %s, NOW(), %s, %s)', 
                       (contraseña_hash, correo, nombre_usuario, id_estado_usuario))
        mysql.connection.commit()
        flash('Usuario registrado con éxito', 'success')
        return redirect(url_for('usuarios'))

    return render_template('usuarios.html')

# Validación de la contraseña
def validate_password(password):
    if len(password) < 8 or len(password) > 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    return True

# Página principal después del inicio de sesión
@app.route('/index')
def index():
    role = session.get('role', 'default')
    allowed_tables = session.get('allowed_tables', [])
    nav_role = session.get('nav_role')
    return render_template('index.html', role=role, allowed_tables=allowed_tables, nav_role=nav_role)

# Página para mostrar tablas autorizadas
@app.route('/<table>')
def show_table(table):
    role = session.get('role', 'default')
    allowed_tables = session.get('allowed_tables', [])
    nav_role = session.get('nav_role')
    if table in allowed_tables:
        return render_template(f'{table}.html', role=role, allowed_tables=allowed_tables, nav_role=nav_role)
    else:
        return "No autorizado", 403
    

if __name__ == '__main__':
    app.run(debug=True)
