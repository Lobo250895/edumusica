from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, send_file
from flask import current_app
import os
from werkzeug.utils import secure_filename
from Conexion import bd  
from functools import wraps
import bcrypt
from datetime import datetime , timedelta
import pymysql
from docx import Document
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_jwt_extended import unset_jwt_cookies
import requests
import subprocess
import psutil
import time
from authlib.integrations.flask_client import OAuth
from flask import send_from_directory
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
from authlib.integrations.flask_client import OAuth
import math
from sync_system.firebase_config import init_firebase
import logging
from logging.handlers import RotatingFileHandler
import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import subprocess
import time
import psutil
import traceback
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import db
from sync_system.firebase_config import init_firebase
from api_docentes.app import create_app, db
from api_docentes.scheduler import iniciar_scheduler
from api_docentes.app.routes import api_blueprint, web_blueprint
from google.oauth2.credentials import Credentials
from gcs_uploader import subir_a_gcs_por_tipo
from gcs_uploader import BUCKET_NAME
from google.cloud import storage
from urllib.parse import urlparse, unquote

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'clave_por_defecto')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'clave_por_defecto')
jwt = JWTManager(app)

# --- Sesiones
app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'
app.config['SESSION_COOKIE_SECURE'] = False  # True en producción
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

# --- Configuración de uploads 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Ruta absoluta

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['PROFILE_UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'profile')
app.config['UPLOAD_INSTRUMENTOS'] = os.path.join(app.config['UPLOAD_FOLDER'], 'instrumentos')
app.config['UPLOAD_LUTHIERS'] = os.path.join(app.config['UPLOAD_FOLDER'], 'luthiers')
app.config['BLOG_UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'blog')
app.config['MUSIC_UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'musica')
app.config['VIDEO_UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'video')
app.config['DOCUMENT_UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'documentos')
app.config['PROJECT_UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'proyectos')
app.config['RECORDING_UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'grabaciones')
app.config['INSPIRACION_UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'inspiracion')
app.config['DISEÑOS_UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'diseños')

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# --- Extensiones permitidas
ALLOWED_EXTENSIONS = {'docx', 'pdf','txt', 'jpg', 'jpeg', 'png', 'gif', 'mp3','mp4', 'webm', 'ogg'}

# Cargar configuración de base de datos y otras cosas importantes
app.config.from_object('api_docentes.config.Config')

# Inicializar extensiones
db.init_app(app)
app.register_blueprint(api_blueprint, url_prefix="/api")      # Para la API
app.register_blueprint(web_blueprint, url_prefix="/web")      # Para el HTML de la API
# Iniciar tareas programadas
iniciar_scheduler()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#api de noticias sobre musica : https://gnews.io
API_KEY = os.getenv('GNEWS_API_KEY')

# Inicializa Firebase al inicio de la aplicación
firebase_db = init_firebase()  


def setup_logging(app):
    import sys

    log_dir = os.path.join(app.root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Evitar handlers repetidos
    if app.logger.hasHandlers():
        app.logger.handlers.clear()

    # Definir nivel según entorno
    if app.debug:
        log_level = logging.DEBUG
        werkzeug_level = logging.DEBUG
    else:
        log_level = logging.WARNING
        werkzeug_level = logging.WARNING

    app.logger.setLevel(log_level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
    )

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Handler consola solo en debug
    if app.debug:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        app.logger.addHandler(console_handler)

    # Configurar logger Flask app
    app.logger.addHandler(file_handler)

    # Configurar logger werkzeug (requests HTTP)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(werkzeug_level)

    # Quitar handlers previos y agregar file_handler (evita duplicados)
    if werkzeug_logger.hasHandlers():
        werkzeug_logger.handlers.clear()
    werkzeug_logger.addHandler(file_handler)

    # Redirigir stdout y stderr a logger solo en producción
    if not app.debug:
        sys.stdout = StreamToLogger(app.logger, logging.INFO)
        sys.stderr = StreamToLogger(app.logger, logging.ERROR)

    app.logger.info('Configuración de logging inicializada')


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass



# Configuración de Google OAuth
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorized_google', _external=True)
    print(f"[DEBUG] Redirect URI usado: {redirect_uri}")  
    return google.authorize_redirect(redirect_uri)


@app.route('/login/google/authorized')
def authorized_google():
    try:
        # Obtiene el token de Google
        token = google.authorize_access_token()

        # ✅ Usa la URL correcta explícitamente
        resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')

        user_info = resp.json()
        google_id = user_info.get('sub')  # OpenID usa 'sub' como ID
        email = user_info.get('email')
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')

        user = bd.seleccionarProfesor(email)
        
        if not user:
            # Si no existe, crea un nuevo usuario
            hashed_password = bcrypt.hashpw(os.urandom(16), bcrypt.gensalt())
            if bd.registrarUsuario(
                name.split()[0] if name else 'Usuario',
                name.split()[1] if name and len(name.split()) > 1 else 'Google',
                '', '', '', email, hashed_password
            ):
                user = bd.seleccionarProfesor(email)
        
        if user:
            # Establece la sesión
            session['email'] = email
            session['id'] = user['id']
            flash('Has iniciado sesión con Google correctamente.', 'success')
            return redirect(url_for('principal'))
        else:
            flash('Error al registrar el usuario de Google.', 'danger')
            return redirect(url_for('login'))
            
    except Exception as e:
        app.logger.error(f"Error en Google OAuth: {repr(e)}")
        app.logger.error(traceback.format_exc())
        flash(f"Error al autenticar con Google: {str(e)}", 'danger')
        return redirect(url_for('login'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:  
            flash("Debes iniciar sesión para acceder a esta página.")  
            return redirect(url_for('login'))  
        return f(*args, **kwargs)
    return decorated_function

init_firebase()  # Inicializa Firebase (una sola vez al iniciar la app)

#################
#  calendar google api
#################

GOOGLE_CLIENT_SECRET_FILE = os.getenv('GOOGLE_CLIENT_SECRET_FILE')

CLIENT_SECRET_FILE = os.path.join(
    os.path.dirname(__file__),
    GOOGLE_CLIENT_SECRET_FILE
)

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

@app.route('/sync')
def sync():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES
    )
    redirect_uri = url_for('callback', _external=True)
    print("🔍 Redirect URI generada:", redirect_uri)  

    flow.redirect_uri = redirect_uri

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    state = session.get('state')
    if not state:
        return redirect(url_for('sync'))

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = url_for('callback', _external=True)

    # Completar token con la respuesta que Google envía al callback
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return redirect(url_for('add_event'))

@app.route('/add_event')
def add_event():
    creds_data = session.get('credentials')
    if not creds_data:
        return redirect('/sync')

    creds = Credentials(**creds_data) 
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': 'Clase de prueba',
        'start': {
            'dateTime': '2025-06-18T10:00:00',
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
        'end': {
            'dateTime': '2025-06-18T11:00:00',
            'timeZone': 'America/Argentina/Buenos_Aires',
        }
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return f"✅ Evento creado: <a href='{created_event.get('htmlLink')}' target='_blank'>Ver en Google Calendar</a>"



# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/entrada', methods=['GET'])
def entrada():
    return render_template('entrada.html')



@app.route('/principal', methods=['GET', 'POST'])
@login_required
def principal():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen


    if request.method == 'POST':
        provincia = request.form.get('provincia', '').strip()
        print(f"Provincia enviada a la API: '{provincia}'")

        if not provincia:
            flash("Por favor ingrese una provincia válida")
            return redirect(url_for('principal'))

        try:
            # 🔁 Llamada interna a la API (sin requests, sin API_URL)
            with current_app.test_client() as client:
                response = client.post(
                    '/api/pago_haberes',
                    json={'provincia': provincia},
                    headers={'Content-Type': 'application/json'}
                )

            if response.status_code == 200:
                data = response.get_json()
                resultados = data.get('results', [])
                session['resultados'] = resultados
                session['buscado'] = True
                if not resultados:
                    flash("No se encontraron resultados para la provincia especificada")
            else:
                error_msg = response.get_json().get('error', 'Error desconocido')
                flash(f"Error en la API: {error_msg}")

        except Exception as e:
            flash(f"Error interno al procesar la solicitud: {str(e)}")
            current_app.logger.error(f"Error interno: {str(e)}")

        return redirect(url_for('principal'))  # Redirige después del POST

    # Método GET
    resultados = session.pop('resultados', None)
    buscado = session.pop('buscado', False)

    return render_template('principal.html', profesor=profesor, resultados=resultados, buscado=buscado)



@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = bd.get_connection()
    if conn is None:
        app.logger.error('No se pudo establecer conexión con la base de datos')
        return render_template("error_db.html")
        
    if request.method == 'POST':
        email = request.form['mail']
        password = request.form['contraseña']
        app.logger.info(f'Intento de login para el email: {email}')
        try:
            user_data = bd.Login_profesor(email, password)
            if user_data:  
                id_usuario, rol = user_data 
                app.logger.info(f'Login exitoso para el usuario: {email} con rol: {rol}')
                
                session['id'] = id_usuario
                session['email'] = email
                session['rol'] = rol
                if rol == 'administrador':
                    return redirect(url_for('administracion'))
                else:  
                    return redirect(url_for('principal'))
                    
            else:
                app.logger.warning(f'Intento fallido de login para: {email}')
                error = "Correo o contraseña incorrectos."
                flash(error)
                
        except Exception as e:
            app.logger.error(f'Error durante el login: {str(e)}', exc_info=True)
            flash("Ocurrió un error durante el login")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.clear()  
    flash("Has cerrado sesión.")
    return redirect(url_for('login'))


@app.route('/contacto', methods=['GET'])
def contacto():
    email = session.get('email')  
    if email:  
        profesor = bd.seleccionarProfesor(email)
        if not profesor:
            profesor = {
                'nombre': "Usuario",
            'apellido': "Desconocido",
            'imagen_perfil': "default.png",
            'id_profesor': None
        }
        bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
        imagen = profesor.get('imagen_perfil') or 'default.png'
        profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

        return render_template('contacto.html', profesor=profesor, usuario_logueado=True)
    else:  
        
        return render_template('contacto.html', profesor=None, usuario_logueado=False)


@app.route('/enviar_contacto', methods=['POST'])
def enviar_contacto():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    asunto = request.form.get('asunto')
    mensaje = request.form.get('mensaje')

    if not all([nombre, email, asunto, mensaje]):
        flash("Todos los campos son obligatorios", "danger")
        return redirect(url_for('contacto'))

    exito = bd.guardar_contacto(nombre, email, asunto, mensaje)
    if exito:
        flash("Tu mensaje ha sido enviado y guardado correctamente. ¡Gracias por contactarnos!", "success")
    else:
        flash("Ocurrió un error al guardar tu mensaje. Inténtalo más tarde.", "danger")

    return redirect(url_for('contacto'))




@app.route('/eliminar_cuenta', methods=['POST'])
@login_required
def eliminar_cuenta():
    id_profesor = session.get('id') 
    email = session.get('email')

    if not id_profesor or not email:
        flash("Debes iniciar sesión primero.")
        return redirect(url_for('login'))

    try:
        bd.eliminar_usuario(id_profesor)  
        session.clear() 
        flash("Cuenta eliminada exitosamente.")
        return redirect(url_for('login'))
    except Exception as e:
        print("Error al eliminar cuenta:", e)
        flash("Hubo un error al eliminar tu cuenta.")
        return redirect(url_for('editar_perfil'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    conn = bd.get_connection()
    if conn is None:
        return render_template("error_db.html")
    
    if request.method == 'POST':
        # 1. Obtener datos del formulario
        email = request.form['mail']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 2. Validaciones básicas
        if password != confirm_password:
            flash('Las contraseñas no coinciden')
            return redirect(url_for('registro'))
            
        if not bd.validar_email(email):
            flash('Email no válido')
            return redirect(url_for('registro'))
            
        if not bd.validar_telefono(telefono):
            flash('Teléfono no válido')
            return redirect(url_for('registro'))


        try:
            # 4. Registrar en Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=f"{nombre} {apellido}"
            )
            firebase_id = user.uid
            
            # 5. Hashear contraseña para MySQL
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # 6. Registrar en MySQL
            if not bd.registrarUsuario(
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                direccion=direccion,
                telefono=telefono,
                email=email,
                hashed_password=hashed_password,
                firebase_id=firebase_id
            ):
                # Revertir Firebase si falla MySQL
                auth.delete_user(firebase_id)
                flash('Error al registrar en nuestra base de datos')
                return redirect(url_for('registro'))

            # 7. Registrar datos adicionales en Firebase Realtime DB
            profesor_data = {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'dni': dni,
                'direccion': direccion,
                'telefono': telefono,
                'fecha_registro': datetime.now().timestamp(),
                'rol': 'profesor'
            }
            
            firebase_db.reference(f'usuarios/{firebase_id}').set(profesor_data)
            
            # 8. Enviar email de verificación
            link = auth.generate_email_verification_link(email)
            # Aquí implementar el envío real del email
            
            # 9. Autenticar al usuario directamente
            session['user'] = {
                'uid': firebase_id,
                'email': email,
                'nombre': nombre,
                'rol': 'profesor'
            }
            
            flash('Registro exitoso. Bienvenido! Inicia Sesion')
            return redirect(url_for('login'))

        except auth.EmailAlreadyExistsError:
            flash('Este email ya está registrado en Firebase')
            return redirect(url_for('registro'))
            
        except Exception as e:
            app.logger.error(f"Error en registro: {str(e)}")
            flash('Error en el sistema de registro. Intente nuevamente.')
            return redirect(url_for('registro'))
    
    return render_template('registro.html')


def registrar_profesor_en_firebase(profesor_data):
    try:
        # Obtiene la referencia a la colección de profesores
        profesores_ref = firebase_db.reference('usuario')
        
        # Crea un nuevo registro en Firebase
        nuevo_profesor_ref = profesores_ref.push()
        nuevo_profesor_ref.set({
            'nombre': profesor_data['nombre'],
            'apellido': profesor_data['apellido'],
            'email': profesor_data['email'],
            'dni': profesor_data['dni'],
            'direccion': profesor_data['direccion'],
            'telefono': profesor_data['telefono'],
            'fecha_registro': datetime.now().timestamp(),
            'activo': True
        })
        
        # Devuelve el ID generado por Firebase
        return nuevo_profesor_ref.key
    except Exception as e:
        app.logger.error(f"Error al registrar profesor en Firebase: {str(e)}")
        return None



@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    email = session['email']
    
    if request.method == 'POST':
        form_type = request.form.get('form_type')   
        try:
            if form_type == 'imagen':
                if 'imagen' not in request.files:
                    flash('No se seleccionó ningún archivo', 'danger')
                    return redirect(url_for('editar_perfil'))

                imagen = request.files['imagen']

                if imagen.filename == '':
                    flash('No se seleccionó ningún archivo', 'danger')
                    return redirect(url_for('editar_perfil'))

                if imagen and allowed_file(imagen.filename):
                    try:
                        _, url_publica = subir_a_gcs_por_tipo(imagen, 'profile')
                        if bd.actualizar_imagen_en_bd(email, url_publica):

                            flash('Imagen de perfil actualizada exitosamente!', 'success')
                        else:
                            flash('Error al actualizar en la base de datos', 'danger')
                    except Exception as e:
                        app.logger.error(f"[ERROR] al subir imagen de perfil: {e}")
                        flash('Error al subir la imagen de perfil', 'danger')
                else:
                    flash('Formato de archivo no permitido', 'danger')

            elif form_type == 'datos':
                nombre = request.form['nombre']
                apellido = request.form['apellido']
                dni = request.form['dni']
                direccion = request.form['direccion']
                telefono = request.form['telefono']
                nuevo_email = request.form['mail']
                nueva_contraseña = request.form.get('contraseña', '').strip()

                if not all([nombre, apellido, dni, direccion, telefono, nuevo_email]):
                    flash('Todos los campos son obligatorios.', 'danger')
                    return redirect(url_for('editar_perfil'))
                if bd.actualizar_datos_profesor(email, nombre, apellido, dni, direccion, telefono, nuevo_email, nueva_contraseña):
                    flash('Datos personales actualizados exitosamente!', 'success')
                    session['email'] = nuevo_email
                else:
                    flash('Error al actualizar los datos personales.', 'danger')
        except Exception as e:
            flash(f'Error al actualizar el perfil: {str(e)}', 'danger')
        return redirect(url_for('editar_perfil'))
    profesor = bd.seleccionarProfesor(email)
    return render_template('editar_perfil.html', profesor=profesor)



@app.route('/mi_inspiracion', methods=['GET', 'POST'])
@login_required
def mi_inspiracion():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401

    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        tipo_archivo = request.form.get('tipo_archivo')
        estado = int(request.form.get('estado', 0))

        if 'file' not in request.files:
            flash("No se envió ningún archivo.", "danger")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash("El archivo no tiene nombre.", "danger")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Tipo de archivo no permitido.", "danger")
            return redirect(request.url)

        # Subo el archivo al bucket, la función devuelve (nombre_seguro, url_publica)
        nombre_seguro, url_publica = subir_a_gcs_por_tipo(file, 'inspiracion')

        try:
            exito = bd.insertar_archivos_profesor(id_profesor, nombre, url_publica, tipo_archivo, estado)
            if not exito:
                flash("No se pudo guardar el archivo en la base de datos.", "danger")
                return redirect(request.url)

            if tipo_archivo.lower() == 'mp3' and estado == 1:
                titulo = nombre  
                artista = "Desconocido" 
                album = "Varios"  
                bd.insertar_cancion(titulo, artista, album, url_publica, "compartido")

            flash("Archivo insertado exitosamente.", "success")
            return redirect(url_for('mi_inspiracion'))
        except Exception as e:
            flash(f"Error al insertar archivo: {str(e)}", "danger")
            return redirect(request.url)

    canciones = bd.obtener_canciones()
    archivos = bd.obtener_archivos_profesor(id_profesor) if id_profesor else []

    return render_template(
        'mi_inspiracion.html',
        canciones=canciones,
        profesor=profesor,
        archivos=archivos
    )


@app.route('/guardar_txt', methods=['POST'])
@login_required
def guardar_txt():
    data = request.get_json()
    ruta = data.get('ruta')
    contenido = data.get('contenido', '')

    if not ruta:
        return jsonify({"error": "Ruta no especificada"}), 400

    if not ruta.endswith(('.txt', '.md', '.log')):
        return jsonify({"error": "Solo se permiten archivos de texto"}), 400

    try:
        if ruta.startswith("https://storage.googleapis.com/"):
            partes = ruta.split(f"{BUCKET_NAME}/")
            if len(partes) != 2:
                return jsonify({"error": "Ruta de archivo inválida"}), 400
            blob_name = partes[1]  
        else:
            blob_name = f"inspiracion/{os.path.basename(ruta)}"
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(contenido, content_type='text/plain')

        return jsonify({"message": "Archivo guardado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error al guardar el archivo: {str(e)}"}), 500


def generar_url_firmada(ruta_blob, expiracion_min=10):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(ruta_blob)

    url_firmada = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiracion_min),
        method="GET"
    )
    return url_firmada



@app.route('/url_firmada')
@login_required
def url_firmada():
    ruta = request.args.get('ruta')
    if not ruta:
        return jsonify({"error": "Ruta no especificada"}), 400

    try:
        if ruta.startswith("https://storage.googleapis.com/"):
            parsed = urlparse(ruta)
            path = parsed.path  
            parts = path.split('/', 2) 
            if len(parts) < 3:
                return jsonify({"error": "Ruta inválida"}), 400
            blob_name = unquote(parts[2])  
        else:
            blob_name = f"inspiracion/{os.path.basename(ruta)}"

        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)
        if not blob.exists():
            return jsonify({"error": "El archivo no existe en GCS"}), 404
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=10),
            method="GET"
        )
        return jsonify({"url": url})
    except Exception as e:
        print(f"Error generando URL firmada: {e}")
        return jsonify({"error": f"No se pudo generar la URL: {str(e)}"}), 500


@app.route('/cambiar_estado_archivo', methods=['POST'])
@login_required
def cambiar_estado_archivo():
    id_profesor = session.get('id')
    email = session.get('email')
    
    try:
        id_archivo = request.form.get('id_archivo')
        nuevo_estado = request.form.get('nuevo_estado')
        
        if not id_archivo or not nuevo_estado:
            return jsonify({"error": "Datos incompletos"}), 400
            
        if nuevo_estado not in ('0', '1'):
            return jsonify({"error": "Estado inválido"}), 400

        if not bd.verificar_ownership_archivo(id_archivo, id_profesor):
            return jsonify({"error": "No autorizado"}), 403

        archivo = bd.obtener_archivo_por_id(id_archivo)
        if not archivo:
            return jsonify({"error": "Archivo no encontrado"}), 404

        # Actualizar estado
        if bd.actualizar_estado_archivo(id_archivo, nuevo_estado):
            # Si es un MP3 y se marca como público, insertar en canciones
            if archivo['tipo_archivo'].lower() == 'mp3' and nuevo_estado == '1':
                bd.insertar_cancion(
                    titulo=archivo['nombre'],
                    artista="Desconocido",
                    album="Varios",
                    ruta_archivo=archivo['ruta_archivo'],
                    categoria="compartido"
                )
            # Si se marca como privado, eliminar de canciones si existe
            elif archivo['tipo_archivo'].lower() == 'mp3' and nuevo_estado == '0':
                bd.eliminar_cancion_por_ruta(archivo['ruta_archivo'])
            
            return jsonify({
                "success": True, 
                "nuevo_estado": int(nuevo_estado),
                "nuevo_estado_texto": "Público" if nuevo_estado == '1' else "Privado"
            })
        else:
            return jsonify({"error": "Error al actualizar"}), 500
            
    except Exception as e:
        app.logger.error(f"Error cambiando estado archivo: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
    

@app.route('/eliminar_archivo', methods=['POST'])
@login_required
def eliminar_archivo():
    id_profesor = session.get('id')
    email = session.get('email')
    
    try:
        id_archivo = request.form.get('id_archivo')
        ruta_archivo = request.form.get('ruta_archivo')

        if not id_archivo or not ruta_archivo:
            return jsonify({"error": "Datos incompletos"}), 400

        # Eliminar de BD primero
        if bd.eliminar_archivo_inspiracion(id_archivo, id_profesor):
            # Eliminar archivo del bucket
            try:
                # Si es una URL pública
                if ruta_archivo.startswith("https://storage.googleapis.com/"):
                    partes = ruta_archivo.split(f"{BUCKET_NAME}/")
                    if len(partes) != 2:
                        raise ValueError("Ruta inválida")
                    blob_name = partes[1]
                else:
                    # Ruta relativa antigua
                    blob_name = f"inspiracion/{os.path.basename(ruta_archivo)}"

                client = storage.Client()
                bucket = client.bucket(BUCKET_NAME)
                blob = bucket.blob(blob_name)
                blob.delete()
            except Exception as ex:
                app.logger.warning(f"No se pudo eliminar el archivo en GCS: {ex}")

            return jsonify({"success": True})
        else:
            return jsonify({"error": "Archivo no encontrado"}), 404

    except Exception as e:
        app.logger.error(f"Error eliminando archivo: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/musica', methods=['GET', 'POST'])
@login_required
def musica():
    email = session.get('email')  
    if not email:  
        return redirect(url_for('login'))
    
    profesor = bd.seleccionarProfesor(email)
    if not profesor:
        profesor = {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    # Obtener canciones de ambas fuentes
    canciones_bd = bd.obtener_canciones()  # Las que ya están en la tabla canciones
    canciones_publicas = bd.obtener_canciones_publicas()  # De inspiración
    
    # Combinar las listas
    canciones = list(canciones_bd) + list(canciones_publicas)
    
    conteo_generos = bd.obtener_conteo_canciones_por_genero()

    artist_info = None
    albums = []
    
    if request.method == "POST":
        artist_name = request.form["artist"]
        url = f"https://musicbrainz.org/ws/2/artist/?query={artist_name}&fmt=json"
        headers = {"User-Agent": "MusicApp/1.0 (your-email@example.com)"}
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if "artists" in data and len(data["artists"]) > 0:
            artist_info = data["artists"][0] 
            artist_id = artist_info["id"]
            albums_url = f"https://musicbrainz.org/ws/2/release-group?artist={artist_id}&fmt=json"
            albums_response = requests.get(albums_url, headers=headers)
            albums_data = albums_response.json()
            
            if "release-groups" in albums_data:
                albums = albums_data["release-groups"]
    
    return render_template(
        'musica.html', 
        canciones=canciones,
        conteo_generos=conteo_generos,
        profesor=profesor, 
        artist_info=artist_info, 
        albums=albums
    )
@app.route('/adjuntar_musica', methods=['GET', 'POST'])
@login_required
def adjuntar_musica():
    email = session.get('email')  
    if not email:  
        return redirect(url_for('login'))
    
    profesor = bd.seleccionarProfesor(email)
    if not profesor:
        profesor = {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    canciones = bd.obtener_canciones()
    canciones_publicas = bd.obtener_canciones_publicas()
    canciones_combinadas = list(canciones) + list(canciones_publicas)
    conteo_generos = bd.obtener_conteo_canciones_por_genero()
    artist_info = None
    albums = []

    if request.method == 'POST':
        titulo = request.form['titulo']
        artista = request.form['artista']
        album = request.form['album']
        categoria = request.form['categoria']
        archivo = request.files['archivo']

        if archivo and archivo.filename != '':
            if allowed_file(archivo.filename):  
                try:
                    # Subir el archivo a Google Cloud Storage
                    nombre_seguro, url_publica = subir_a_gcs_por_tipo(archivo, 'musica')
                except Exception as e:
                    app.logger.error(f"Error al subir música a GCS: {str(e)}")
                    flash('Error al subir la canción al almacenamiento.', 'danger')
                    return render_template('musica.html', profesor=profesor, canciones=canciones_combinadas, conteo_generos=conteo_generos, artist_info=artist_info, albums=albums)

                try:
                    # Guardar en la base de datos
                    bd.crear_musica(titulo, artista, album, url_publica, categoria)
                    flash('Archivo subido exitosamente.', 'success')
                    return redirect(url_for('musica'))
                except Exception as e:
                    app.logger.error(f"Error al guardar en la base de datos: {str(e)}")
                    flash('Error al guardar la canción en la base de datos.', 'danger')
                    return render_template('musica.html', profesor=profesor, canciones=canciones_combinadas, conteo_generos=conteo_generos, artist_info=artist_info, albums=albums)
            else:
                flash('Tipo de archivo no permitido.', 'danger')
        else:
            flash('No se seleccionó ningún archivo.', 'danger')
    return render_template('musica.html', profesor=profesor, canciones=canciones_combinadas, conteo_generos=conteo_generos, artist_info=artist_info, albums=albums)


@app.route('/proyectos', methods=['GET', 'POST'])
@login_required
def proyectos():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No hay archivo para subir.', 'error')
            return redirect(url_for('proyectos'))

        file = request.files['file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo.', 'error')
            return redirect(url_for('proyectos'))

        if allowed_file(file.filename):
            _, archivo_url = subir_a_gcs_por_tipo(file, 'proyectos')

            nombre = request.form['nombre']
            estado = request.form['estado']
            es_publico = int(request.form.get('es_publico', 0))

            profesor = bd.seleccionarProfesor(email)
            if not profesor or 'id' not in profesor or profesor['id'] is None:
                flash("Error: No se encontró al profesor.", "error")
                return redirect(url_for('proyectos'))

            autor = bd.obtener_nombre_profesor(email)
            autor_id = profesor['id']
            fecha_subida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Debug de tipos y valores antes de insertar
            #print("Insertar proyecto con datos:")
            #print(f"nombre={nombre} ({type(nombre)})")
            #print(f"autor={autor} ({type(autor)})")
            #print(f"fecha_subida={fecha_subida} ({type(fecha_subida)})")
            #print(f"proyecto={archivo_url} ({type(archivo_url)})")
            #print(f"estado={estado} ({type(estado)})")
            #print(f"es_publico={es_publico} ({type(es_publico)})")
            #print(f"autor_id={autor_id} ({type(autor_id)})")

            try:
                bd.insertar_proyecto(nombre, autor, fecha_subida, archivo_url, estado, es_publico, autor_id)
                flash('Proyecto subido exitosamente.', 'success')
                return redirect(url_for('proyectos'))
            except pymysql.MySQLError as e:
                flash(f'Error al insertar el proyecto: {e}', 'error')
                return redirect(url_for('proyectos'))
        else:
            flash('Tipo de archivo no permitido.', 'error')
        return redirect(url_for('proyectos'))

    proyectos = bd.obtener_todos_los_proyectos()
    profesor = bd.seleccionarProfesor(email)
    proyectos_propios = []
    proyectos_publicos = []
    proyectos_admin = bd.obtener_proyectos_del_administrador()

    for proyecto in proyectos:
        if proyecto.get('autor_id') == profesor['id']:
            proyectos_propios.append(proyecto)
        elif proyecto.get('es_publico') == 1 and proyecto.get('autor_id') != 2:
            proyectos_publicos.append(proyecto)

    return render_template('proyectos.html',
                           proyectos_propios=proyectos_propios,
                           proyectos_publicos=proyectos_publicos,
                           profesor=profesor,
                           proyectos_admin=proyectos_admin)


@app.route('/proyectos/eliminar', methods=['DELETE'])
@login_required
def eliminar_proyecto():
    data = request.get_json()
    proyecto_id = data.get('proyecto_id')

    if not proyecto_id:
        return jsonify({'success': False, 'message': 'ID de proyecto no proporcionado'}), 400

    email = session.get('email')
    profesor = bd.seleccionarProfesor(email)
    if not profesor:
        return jsonify({'success': False, 'message': 'Profesor no encontrado'}), 403

    autor_id = profesor['id']
    proyecto = bd.obtener_proyecto_por_id(proyecto_id)

    if not proyecto or proyecto['autor_id'] != autor_id:
        return jsonify({'success': False, 'message': 'No tienes permiso para eliminar este proyecto'}), 403
    try:
        ruta_completa = proyecto['proyecto']
        if ruta_completa.startswith("https://storage.googleapis.com/"):
            partes = ruta_completa.split(f"{BUCKET_NAME}/")
            blob_name = partes[1] if len(partes) == 2 else f"proyectos/{os.path.basename(ruta_completa)}"
        else:
            blob_name = f"proyectos/{os.path.basename(ruta_completa)}"

        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)
        if blob.exists():
            blob.delete()
    except Exception as e:
        print(f"Error al eliminar archivo de GCS: {e}")
    if bd.eliminar_proyecto(proyecto_id, autor_id):
        return jsonify({'success': True, 'message': 'Proyecto eliminado correctamente'})
    else:
        return jsonify({'success': False, 'message': 'Error al eliminar el proyecto'}), 500




@app.route('/proyectos/<int:proyecto_id>/comentarios')
def obtener_comentarios(proyecto_id):
    try:
        comentarios = bd.obtener_comentarios_proyecto(proyecto_id)
        if comentarios is None:
            return jsonify({"error": "Error al obtener comentarios"}), 500

        comentarios_jerarquicos = bd.estructurar_comentarios_en_arbol(comentarios)
        return jsonify(comentarios_jerarquicos)
    except Exception as e:
        print(f"Error en endpoint /proyectos/comentarios: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
    

@app.route('/comentarios/nuevo', methods=['POST'])
@login_required
def nuevo_comentario():
    email = session.get('email')

    profesor = bd.seleccionarProfesor(email)
    if not profesor:
        return jsonify({'success': False, 'error': 'Usuario no encontrado'})

    data = request.get_json()
    proyecto_id = data.get('proyecto_id')
    contenido = data.get('contenido')
    comentario_padre_id = data.get('comentario_padre_id') 

    nuevo_id = bd.insertar_comentario(proyecto_id, profesor['id'], contenido, comentario_padre_id)
    flash('comentario subido exitosamente.', 'success')

    if nuevo_id:
        return jsonify({'success': True, 'comentario_id': nuevo_id})
    else:
        return jsonify({'success': False, 'error': 'No se pudo insertar'})


@app.route('/uploads/proyectos/<int:id>')
@login_required
def uploaded_file(id):
    proyecto = bd.obtener_detalles_proyecto(id)
    if not proyecto:
        return "Proyecto no encontrado", 404
    archivo_url = proyecto.get('archivo_url')
    if not archivo_url:
        return "Archivo no encontrado", 404
    return redirect(archivo_url)



@app.route('/reproductor')
@login_required
def reproductor():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    genero = request.args.get('genero')  
    canciones = bd.obtener_canciones_por_genero(genero)
    
    return render_template('reproductor.html', profesor=profesor,genero=genero, canciones=canciones)



@app.route('/get_canciones')
@login_required
def get_canciones():
    canciones = bd.obtener_canciones()
    print(canciones)
    if canciones:  
        canciones_json = [{"id": cancion['id'], "titulo": cancion['titulo'], "artista": cancion['artista'], "ruta_archivo": cancion['ruta_archivo']} for cancion in canciones]
        return jsonify({"canciones": canciones_json})
    else:
        return jsonify({"error": "No se encontraron canciones."}), 500

@app.route('/agenda')
@login_required
def agenda():
    id_profesor = session.get('id')
    email = session.get('email')

    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401

    # Obtener información del profesor
    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
            'apellido': "Desconocido",
            'imagen_perfil': "default.png",
            'id_profesor': None
        }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    # Obtener eventos para el profesor
    eventos = bd.obtenereventos(id_profesor)
    
    # Convertir eventos a formato serializable
    eventos_dict = []
    if eventos:
        for evento in eventos:
            eventos_dict.append({
                'id': evento.get('id'),
                'titulo': evento.get('titulo'),
                'tipo': evento.get('tipo'),
                'fecha': evento.get('fecha').strftime('%Y-%m-%d') if evento.get('fecha') and evento.get('fecha') != '0000-00-00' else None,
                'hora_inicio': str(evento.get('hora_inicio')) if evento.get('hora_inicio') else None,
                'hora_fin': str(evento.get('hora_fin')) if evento.get('hora_fin') else None,
                'lugar': evento.get('lugar'),
                'descripcion': evento.get('descripcion')
            })

    # Obtener escuelas del profesor
    escuelas = bd.obtener_escuelas_profesor(id_profesor)
    
    # Convertir escuelas a formato serializable
    escuelas_dict = []
    if escuelas:
        for escuela in escuelas:
            escuelas_dict.append({
                'id_escuela': escuela.get('id_escuela'),
                'nombre_escuela': escuela.get('nombre_escuela'),
                'direccion': escuela.get('direccion'),
                'telefono': escuela.get('telefono'),
                'fecha_inicio': escuela.get('fecha_inicio').strftime('%Y-%m-%d') if escuela.get('fecha_inicio') else None,
                'fecha_cese': escuela.get('fecha_cese').strftime('%Y-%m-%d') if escuela.get('fecha_cese') else None
            })

    # Obtener reportes del profesor
    reportes = bd.obtener_reportes_profesor(id_profesor)
    
    # Convertir reportes a formato serializable
    reportes_dict = []
    if reportes:
        for reporte in reportes:
            reportes_dict.append({
                'id_reporte': reporte.get('id_reporte'),
                'id_escuela': reporte.get('id_escuela'),
                'nombre_alumno': reporte.get('nombre_alumno'),
                'apellido_alumno': reporte.get('apellido_alumno'),
                'tipo': reporte.get('tipo'),
                'fecha_reporte': reporte.get('fecha_reporte').strftime('%Y-%m-%d') if reporte.get('fecha_reporte') else None,
                'descripcion': reporte.get('descripcion'),
                # Agregar nombre de la escuela si es posible
                'nombre_escuela': next((esc['nombre_escuela'] for esc in escuelas_dict if esc['id_escuela'] == reporte.get('id_escuela')), None)
            })
    return render_template('agenda.html', 
                         profesor=profesor, 
                         eventos=eventos_dict,
                         escuelas=escuelas_dict,
                         reportes=reportes_dict)


@app.route('/escuelas/listar')
@login_required
def listar_escuelas():
    id_profesor = session.get('id')
    escuelas = bd.obtener_escuelas_profesor(id_profesor)
    
    escuelas_dict = []
    for escuela in escuelas:
        escuelas_dict.append({
            'id_escuela': escuela.get('id_escuela'),
            'nombre_escuela': escuela.get('nombre_escuela'),
            'direccion': escuela.get('direccion'),
            'telefono': escuela.get('telefono'),
            'fecha_inicio': escuela.get('fecha_inicio').strftime('%Y-%m-%d') if escuela.get('fecha_inicio') else None,
            'fecha_cese': escuela.get('fecha_cese').strftime('%Y-%m-%d') if escuela.get('fecha_cese') else None
        })
    
    return jsonify(escuelas_dict)

@app.route('/reportes/listar')
@login_required
def listar_reportes():
    id_profesor = session.get('id')
    reportes = bd.obtener_reportes_profesor(id_profesor)
    escuelas = bd.obtener_escuelas_profesor(id_profesor)
    
    reportes_dict = []
    for reporte in reportes:
        reportes_dict.append({
            'id_reporte': reporte.get('id_reporte'),
            'id_escuela': reporte.get('id_escuela'),
            'nombre_alumno': reporte.get('nombre_alumno'),
            'apellido_alumno': reporte.get('apellido_alumno'),
            'tipo': reporte.get('tipo'),
            'fecha_reporte': reporte.get('fecha_reporte').strftime('%Y-%m-%d') if reporte.get('fecha_reporte') else None,
            'descripcion': reporte.get('descripcion'),
            'nombre_escuela': next((esc['nombre_escuela'] for esc in escuelas if esc['id_escuela'] == reporte.get('id_escuela')), None)
        })
    
    return jsonify(reportes_dict)


@app.route('/escuela/crear', methods=['POST'])
@login_required
def crear_escuela():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            required_fields = ['nombre_escuela', 'direccion', 'fecha_inicio']
            if not all(data.get(field) for field in required_fields):
                return jsonify({'success': False, 'error': 'Faltan campos requeridos'}), 400
            
            # Validar fechas
            fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d')
            if data.get('fecha_cese'):
                fecha_cese = datetime.strptime(data['fecha_cese'], '%Y-%m-%d')
                if fecha_cese < fecha_inicio:
                    return jsonify({'success': False, 'error': 'La fecha de cese debe ser posterior a la de inicio'}), 400
            
            # Datos adicionales
            data.update({
                'id_usuario': session.get('id'),
                'fecha_creacion': datetime.now().strftime('%Y-%m-%d')
            })
            
            # Insertar en la base de datos
            escuela_id = bd.insertar_escuelas(**data)
            flash("Escuela agregada correctamente", "escuela_success")
            
            return jsonify({'success': True, 'id': escuela_id})
        
        except ValueError as e:
            flash("Error al agregar escuela", "escuela_error")
            return jsonify({'success': False, 'error': 'Formato de fecha inválido'}), 400
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        
        
@app.route('/escuela/actualizar/<int:id_escuela>', methods=['PUT'])
@login_required
def actualizar_escuela(id_escuela):
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['nombre_escuela', 'direccion', 'fecha_inicio']
        if not all(data.get(field) for field in required_fields):
            return jsonify({'success': False, 'error': 'Faltan campos requeridos'}), 400
        
        # Convertir fechas
        try:
            fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
            fecha_cese = datetime.strptime(data['fecha_cese'], '%Y-%m-%d').date() if data.get('fecha_cese') else None
        except ValueError as e:
            return jsonify({'success': False, 'error': 'Formato de fecha inválido'}), 400
        
        # Actualizar en la base de datos
        filas_afectadas = bd.actualizar_escuela(
            id_escuela=id_escuela,
            nombre_escuela=data['nombre_escuela'],
            direccion=data['direccion'],
            telefono=data.get('telefono'),
            fecha_inicio=fecha_inicio,
            fecha_cese=fecha_cese,
            usuario_id=session.get('id')
        )
        
        if filas_afectadas == 0:
            return jsonify({'success': False, 'error': 'Escuela no encontrada o no tienes permisos'}), 404
        
        # Devolver la escuela actualizada
        escuela_actualizada = bd.obtener_escuela_por_id(id_escuela, session.get('id'))
        if not escuela_actualizada:
            return jsonify({'success': False, 'error': 'Error al obtener escuela actualizada'}), 500
            
        # Formatear respuesta
        escuela_serializable = {
            'id_escuela': escuela_actualizada.get('id_escuela'),
            'nombre_escuela': escuela_actualizada.get('nombre_escuela'),
            'direccion': escuela_actualizada.get('direccion'),
            'telefono': escuela_actualizada.get('telefono'),
            'fecha_inicio': escuela_actualizada.get('fecha_inicio').strftime('%Y-%m-%d') if escuela_actualizada.get('fecha_inicio') else None,
            'fecha_cese': escuela_actualizada.get('fecha_cese').strftime('%Y-%m-%d') if escuela_actualizada.get('fecha_cese') else None
        }
        
        return jsonify({'success': True, 'escuela': escuela_serializable})
    
    except Exception as e:
        app.logger.error(f'Error al actualizar escuela {id_escuela}: {str(e)}', exc_info=True)
        return jsonify({
            'success': False, 
            'error': f'Error interno al actualizar la escuela: {str(e)}'
        }), 500
    

@app.route('/escuela/eliminar/<int:id_escuela>', methods=['DELETE'])
@login_required
def eliminar_escuela(id_escuela):
    try:
        # Verificar si la escuela existe y pertenece al usuario
        escuela = bd.obtener_escuela_por_id(id_escuela, session.get('id'))
        if not escuela:
            return jsonify({
                'success': False, 
                'error': 'Escuela no encontrada o no tienes permisos'
            }), 404
        
        # Eliminar reportes asociados primero
        reportes_eliminados = bd.eliminar_reportes_de_escuela(id_escuela)
        app.logger.info(f"Eliminados {reportes_eliminados} reportes de la escuela {id_escuela}")
        
        # Luego eliminar la escuela
        filas_afectadas = bd.eliminar_escuela(id_escuela, session.get('id'))

        if filas_afectadas == 0:
            return jsonify({
                'success': False, 
                'error': 'No se pudo eliminar la escuela'
            }), 400
            
        return jsonify({
            'success': True, 
            'message': 'Escuela eliminada correctamente',
            'reportes_eliminados': reportes_eliminados
        })
    except Exception as e:
        app.logger.error(f'Error al eliminar escuela {id_escuela}: {str(e)}')
        return jsonify({
            'success': False, 
            'error': 'Error interno al eliminar la escuela'
        }), 500


@app.route('/reporte/crear', methods=['POST'])
@login_required
def crear_reporte():
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json',
                'message': 'El request debe ser en formato JSON'
            }), 400
        data = request.get_json()
        if 'id' not in session:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Usuario no autenticado'
            }), 401
        reporte_data = {
            'tipo': data.get('tipo'),
            'descripcion': data.get('descripcion'),
            'fecha_reporte': data.get('fecha_reporte'),
            'estado': "Regular",
            'id_escuela': data.get('id_escuela'),
            'id_usuario': session.get('id'),
            'nombre_alumno': data.get('nombre_alumno'),
            'apellido_alumno': data.get('apellido_alumno')
        }
        required_fields = ['tipo', 'descripcion', 'fecha_reporte', 'id_escuela', 
                         'nombre_alumno', 'apellido_alumno']
        missing_fields = [field for field in required_fields if not reporte_data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}',
                'message': 'Por favor complete todos los campos requeridos'
            }), 400
        tipos_validos = ['conducta', 'academico', 'asistencia', 'felicitacion', 'otro']
        if reporte_data['tipo'] not in tipos_validos:
            return jsonify({
                'success': False,
                'error': 'Tipo de reporte inválido',
                'message': f'Los tipos válidos son: {", ".join(tipos_validos)}'
            }), 400
        try:
            fecha_obj = datetime.strptime(reporte_data['fecha_reporte'], '%Y-%m-%d')
            if fecha_obj.date() > datetime.now().date():
                return jsonify({
                    'success': False,
                    'error': 'Fecha inválida',
                    'message': 'La fecha no puede ser futura'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Formato de fecha inválido',
                'message': 'El formato de fecha debe ser YYYY-MM-DD'
            }), 400
        reporte_id = bd.insertar_reporte(**reporte_data)
        flash("Reporte creado correctamente", "reporte_success")
        
        if not reporte_id:
            raise Exception('Error al insertar el reporte en la base de datos')
        return jsonify({
            'success': True,
            'id': reporte_id,
            'message': 'Reporte creado exitosamente',
            'data': {
                'id_reporte': reporte_id,
                'tipo': reporte_data['tipo'],
                'estado': reporte_data['estado'],
                'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 201

    except Exception as e:
        app.logger.error(f'Error al crear reporte: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno al crear el reporte'
        }), 500


@app.route('/reporte/eliminar/<int:report_id>', methods=['DELETE'])
@login_required
def eliminar_reporte(report_id):
    try:
        reporte = bd.obtener_reporte_por_id(report_id, session.get('id'))
        if not reporte:
            return jsonify({
                'success': False,
                'error': 'Reporte no encontrado o no tienes permisos'
            }), 404

        filas_afectadas = bd.eliminar_reporte(report_id, session.get('id'))
        
        if filas_afectadas == 0:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el reporte'
            }), 400
            
        return jsonify({
            'success': True,
            'message': 'Reporte eliminado correctamente'
        })
    except Exception as e:
        app.logger.error(f'Error al eliminar reporte {report_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Error interno al eliminar el reporte'
        }), 500
    
@app.route('/reporte/actualizar/<int:id_reporte>', methods=['PUT'])
@login_required
def actualizar_reporte(id_reporte):
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
            
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['tipo', 'descripcion', 'fecha_reporte', 'id_escuela', 
                         'nombre_alumno', 'apellido_alumno']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
            }), 400
        
        # Validar fecha
        try:
            fecha_reporte = datetime.strptime(data['fecha_reporte'], '%Y-%m-%d').date()
            if fecha_reporte > datetime.now().date():
                return jsonify({
                    'success': False,
                    'error': 'La fecha no puede ser futura'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Formato de fecha inválido (YYYY-MM-DD)'
            }), 400
        
        # Actualizar reporte
        filas_afectadas = bd.actualizar_reporte(
            id_reporte=id_reporte,
            id_escuela=data['id_escuela'],
            tipo=data['tipo'],
            descripcion=data['descripcion'],
            fecha_reporte=fecha_reporte,
            nombre_alumno=data['nombre_alumno'],
            apellido_alumno=data['apellido_alumno'],
            usuario_id=session.get('id')
        )
        
        if filas_afectadas == 0:
            return jsonify({
                'success': False,
                'error': 'Reporte no encontrado o no tienes permisos'
            }), 404
            
        # Obtener reporte actualizado
        reporte_actualizado = bd.obtener_reporte_por_id(id_reporte, session.get('id'))
        if not reporte_actualizado:
            return jsonify({
                'success': False,
                'error': 'Error al obtener reporte actualizado'
            }), 500
            
        # Formatear respuesta
        reporte_serializable = {
            'id_reporte': reporte_actualizado.get('id_reporte'),
            'id_escuela': reporte_actualizado.get('id_escuela'),
            'nombre_alumno': reporte_actualizado.get('nombre_alumno'),
            'apellido_alumno': reporte_actualizado.get('apellido_alumno'),
            'tipo': reporte_actualizado.get('tipo'),
            'fecha_reporte': reporte_actualizado.get('fecha_reporte').strftime('%Y-%m-%d') if reporte_actualizado.get('fecha_reporte') else None,
            'descripcion': reporte_actualizado.get('descripcion')
        }
        
        return jsonify({'success': True, 'reporte': reporte_serializable})
        
    except Exception as e:
        app.logger.error(f'Error al actualizar reporte {id_reporte}: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Error interno al actualizar el reporte: {str(e)}'
        }), 500

@app.route('/evento/crear', methods=['POST'])
@login_required
def crear_evento():
    data = request.json
    usuario_id = session.get('id')

    bd.insertar_evento(
        profesor_id=usuario_id,
        titulo=data['titulo'],
        tipo=data['tipo'],
        fecha=data['fecha'],
        hora_inicio=data['hora_inicio'],
        hora_fin=data['hora_fin'],
        lugar=data.get('lugar', ''),
        descripcion=data.get('descripcion', ''),
        estado="activo"
    )
    return jsonify({"mensaje": "Evento creado correctamente"}), 201

@app.route('/evento/eliminar/<int:evento_id>', methods=['DELETE'])
@login_required
def eliminar_evento_route(evento_id):
    usuario_id = session.get('id')
    filas_afectadas = bd.eliminar_evento(evento_id, usuario_id)
    if filas_afectadas == 0:
        return jsonify({"error": "No se encontró el evento o no tenés permisos"}), 404
    return jsonify({"mensaje": "Evento eliminado"}), 200

@app.route('/evento/actualizar/<int:evento_id>', methods=['PUT'])
@login_required
def actualizar_evento_route(evento_id):
    data = request.json
    usuario_id = session.get('id')

    filas_afectadas = bd.actualizar_evento(
        evento_id=evento_id,
        usuario_id=usuario_id,
        titulo=data['titulo'],
        tipo=data['tipo'],
        fecha=data['fecha'],
        hora_inicio=data['hora_inicio'],
        hora_fin=data['hora_fin'],
        lugar=data.get('lugar', ''),
        descripcion=data.get('descripcion', ''),
        estado=data.get('estado', 'activo')
    )
    if filas_afectadas == 0:
        return jsonify({"error": "No se encontró el evento o no tenés permisos"}), 404
    return jsonify({"mensaje": "Evento actualizado"}), 200


@app.route('/escuela/<int:id_escuela>')
@login_required
def obtener_escuela(id_escuela):
    try:
        escuela = bd.obtener_escuela_por_id(id_escuela, session.get('id'))
        if not escuela:
            return jsonify({'error': 'Escuela no encontrada'}), 404
        
        escuela_serializable = {
            'id_escuela': escuela.get('id_escuela'),
            'nombre_escuela': escuela.get('nombre_escuela'),
            'direccion': escuela.get('direccion'),
            'telefono': escuela.get('telefono'),
            'fecha_inicio': escuela.get('fecha_inicio').strftime('%Y-%m-%d') if escuela.get('fecha_inicio') else None,
            'fecha_cese': escuela.get('fecha_cese').strftime('%Y-%m-%d') if escuela.get('fecha_cese') else None
        }
        
        return jsonify(escuela_serializable)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reporte/<int:id_reporte>')
@login_required
def obtener_reporte(id_reporte):
    try:
        reporte = bd.obtener_reporte_por_id(id_reporte, session.get('id'))
        if not reporte:
            return jsonify({'error': 'Reporte no encontrado'}), 404
        
        reporte_serializable = {
            'id_reporte': reporte.get('id_reporte'),
            'id_escuela': reporte.get('id_escuela'),
            'nombre_alumno': reporte.get('nombre_alumno'),
            'apellido_alumno': reporte.get('apellido_alumno'),
            'tipo': reporte.get('tipo'),
            'fecha_reporte': reporte.get('fecha_reporte').strftime('%Y-%m-%d') if reporte.get('fecha_reporte') else None,
            'descripcion': reporte.get('descripcion')
        }
        
        return jsonify(reporte_serializable)
    except Exception as e:
        return jsonify({'error': str(e)}), 500        


@app.route('/ayuda')
def ayuda():
    email = session.get('email')  
    if email:  
        profesor = bd.seleccionarProfesor(email)
        if not profesor:
            profesor = {
                'nombre': "Usuario",
            'apellido': "Desconocido",
            'imagen_perfil': "default.png",
            'id_profesor': None
        }
        bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
        imagen = profesor.get('imagen_perfil') or 'default.png'
        profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

        return render_template('ayuda.html', profesor=profesor, usuario_logueado=True)
    else:  
        
        return render_template('ayuda.html', profesor=None, usuario_logueado=False)



@app.route('/educacion')
@login_required
def educacion():
    email = session.get('email')  
    if not email:  
        return redirect(url_for('login'))
    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    recursos = bd.obtener_recursos_por_categoria("diseños")
    return render_template('educacion.html' , profesor=profesor , recursos=recursos)


@app.route('/recursos/<filename>')
def descargar_recurso(filename):
    return send_from_directory(app.config['RECURSOS_UPLOAD_FOLDER'], filename)



@app.route('/videos')
@login_required
def videos():
    email = session.get('email')  
    if not email:  
        return redirect(url_for('login'))

    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    videos = bd.ver_videos()
    
    return render_template('videos.html', profesor=profesor, videos=videos)

        
@app.route('/subir_video', methods=['POST'])
@login_required
def subir_video():
    if request.method == 'POST':
        try:
            if not all(key in request.form for key in ['nombre', 'genero']):
                flash('Faltan campos requeridos en el formulario', 'error')
                return redirect(request.referrer)

            nombre = request.form['nombre']
            genero = request.form['genero']
            video = request.files.get('video')
            miniatura_base64 = request.form.get('miniatura_generada')

            if not video or video.filename == '':
                flash('No se seleccionó ningún video', 'error')
                return redirect(request.referrer)

            # Subir el video a GCS
            video_filename, video_url = subir_a_gcs_por_tipo(video, 'video')

            # Procesar la miniatura si se generó desde el frontend
            imagen_url = None
            if miniatura_base64:
                import base64
                from io import BytesIO
                from PIL import Image
                from werkzeug.datastructures import FileStorage

                # Decodificar imagen desde base64
                header, encoded = miniatura_base64.split(",", 1)
                image_data = base64.b64decode(encoded)
                image = Image.open(BytesIO(image_data))

                # Convertir la imagen a un objeto tipo archivo
                buffer = BytesIO()
                image.save(buffer, format="JPEG")
                buffer.seek(0)

                imagen_file = FileStorage(
                    stream=buffer,
                    filename=f"{video_filename}_thumb.jpg",
                    content_type='image/jpeg'
                )

                # Subir miniatura a GCS
                imagen_filename, imagen_url = subir_a_gcs_por_tipo(imagen_file, 'video')

            # Validar sesión
            profesor_id = session.get('id')
            if not profesor_id:
                flash('No se pudo identificar su sesión', 'error')
                return redirect(url_for('login'))

            # Guardar en base de datos
            if not bd.guardar_video(nombre, video_url, genero, imagen_url, profesor_id):
                raise Exception("Error al guardar en la base de datos")

            # Notificar a todos los profesores
            profesores = bd.obtener_todos_los_profesores()
            for profesor in profesores:
                bd.agregar_notificacion(
                    profesor['id'],
                    f"Nuevo video publicado: {nombre} ({genero})",
                    url_for('videos', video_id=video_filename)
                )

            flash('Video subido exitosamente!', 'success')
            return redirect(url_for('videos'))

        except Exception as e:
            app.logger.error(f"Error al subir video: {str(e)}")
            flash(f'Error al subir el video: {str(e)}', 'error')
            return redirect(request.referrer)




@app.route('/juegos')
@login_required
def juegos():
    email = session.get('email')
    profesor = bd.seleccionarProfesor(email)
    if not profesor:
        profesor = {
            'nombre': "Usuario",
            'apellido': "Desconocido",
            'imagen_perfil': "default.png",
            'id_profesor': None
        }
        bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
        imagen = profesor.get('imagen_perfil') or 'default.png'
        profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    return render_template('juegos.html', profesor=profesor)


@app.route('/guardar_melodia', methods=['POST'])
@login_required
def guardar_melodia():
    try:
        data = request.get_json()
        id_profesor = session.get('id')
        
        # Guardar en base de datos
        #bd.guardar_melodia(
        #    id_profesor,
        #    json.dumps(data),
        #    datetime.now()
        #)
        
        return jsonify({"success": True})
    except Exception as e:
        app.logger.error(f"Error al guardar melodía: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
    

@app.route('/libros', methods=['GET', 'POST'])
@login_required
def libros():
    email = session.get('email')
    id_profesor = session.get('id')
    
    if not email:
        return redirect(url_for('login'))
    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        categoria = request.form.get('categoria')
        nombre = request.form.get('nombre')
        
        if not categoria or not nombre:
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('libros'))
        
        try:
            if categoria == 'web':
                url = request.form.get('url')
                if not url:
                    flash('La URL es requerida para recursos web', 'error')
                    return redirect(url_for('libros'))
                
                bd.guardar_recurso(
                    nombre=nombre,
                    url=url,
                    categoria=categoria,
                    tamanio='N/A'
                )
                flash('Link web guardado correctamente', 'success')
                
            else:
                if 'file' not in request.files:
                    flash('No se seleccionó ningún archivo', 'error')
                    return redirect(url_for('libros'))
                
                file = request.files['file']
                if file.filename == '':
                    flash('No se seleccionó ningún archivo', 'error')
                    return redirect(url_for('libros'))
                
                if file and allowed_file(file.filename):
                    archivo_url = subir_a_gcs_por_tipo(file, categoria)
                    file.seek(0, os.SEEK_END)  
                    tamanio = file.tell()
                    file.seek(0)  
                    tamanio_str = f"{tamanio/1024:.2f} KB" if tamanio < 1024*1024 else f"{tamanio/(1024*1024):.2f} MB"
                    bd.guardar_recurso(
                        nombre=nombre,
                        url=archivo_url,
                        categoria=categoria,
                        tamanio=tamanio_str
                    )
                    flash('Archivo subido correctamente', 'success')
                else:
                    flash('Tipo de archivo no permitido', 'error')
        
        except Exception as e:
            app.logger.error(f"Error al guardar recurso: {str(e)}")
            flash('Error al guardar el recurso', 'error')
        
        return redirect(url_for('libros'))

    pagina = int(request.args.get('pagina', 1))
    por_pagina = 10
    todos_los_links = bd.obtener_recursos_por_categoria('web')
    total_paginas = math.ceil(len(todos_los_links) / por_pagina)
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    recursos_web = todos_los_links[inicio:fin]

    recursos_peliculas = bd.obtener_recursos_por_categoria('peliculas')

    recursos_libros = bd.obtener_recursos_por_categoria('libros')

    return render_template(
        'libros.html', 
        profesor=profesor,
        recursos_web=recursos_web,
        recursos_peliculas=recursos_peliculas,
        recursos_libros=recursos_libros,
        categoria_actual=request.args.get('categoria', 'web'),
        pagina_actual=pagina,
        total_paginas=total_paginas
    )


def is_process_running(process_name):
    return process_name.lower() in (p.name().lower() for p in psutil.process_iter())


@app.route('/blog')
@login_required
def blog():
    email = session.get('email')  
    id_profesor = session.get('id')  
    
    if not email: 
        return redirect(url_for('login'))
    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    blogs = bd.obtener_blog()
    for blog in blogs:
        estadisticas = bd.obtener_estadisticas(blog['id'])
        blog['estadisticas'] = estadisticas  
    
    url = f'https://gnews.io/api/v4/search?q=coldplay&lang=es&max=1&token={API_KEY}'
    response = requests.get(url)
    data = response.json()
    noticia = data['articles'][0] if data.get('articles') else None
    
    return render_template('blog.html', profesor=profesor, blogs=blogs , noticia=noticia)

def organizar_comentarios(comentarios):
    comentario_dict = {comentario['id']: comentario for comentario in comentarios}

    for comentario in comentarios:
        comentario['respuestas'] = []
        if 'parent_id' not in comentario or comentario['parent_id'] is None:
            comentario['parent_id'] = None  

    estructura = []
    for comentario in comentarios:
        if comentario['parent_id']:  # si es respuesta
            parent = comentario_dict.get(comentario['parent_id'])
            if parent:
                parent['respuestas'].append(comentario)
        else:
            estructura.append(comentario)

    return estructura


@app.route('/blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def ver_blog(blog_id):
    email = session.get('email')  
    id_profesor = session.get('id')  

    if not email: 
        return redirect(url_for('login'))

    profesor = bd.seleccionarProfesor(email) or {
            'nombre': "Usuario",
            'apellido': "Desconocido",
            'imagen_perfil': "default.png",
            'id_profesor': None
        }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen
    
    blog = bd.obtener_blog_por_id(blog_id)
    comentarios = bd.obtener_comentarios(blog_id) 
    comentarios_organizados = organizar_comentarios(comentarios)
    estadisticas = bd.obtener_estadisticas(blog_id)

    if not blog:
        return "El blog no existe", 404

    if 'blogs_vistos' not in session:
        session['blogs_vistos'] = []

    if blog_id not in session['blogs_vistos']:
        bd.incrementar_vistas(blog_id)
        session['blogs_vistos'].append(blog_id)
    
    usuario_actual = bd.seleccionar_usuario_por_id(id_profesor)

    if request.method == 'POST':
        if 'comentario' in request.form:
            comentario = request.form.get('comentario')
            parent_id = request.form.get('parent_id') 
            if comentario:
                bd.agregar_comentario(blog_id, session['id'], comentario, parent_id)
                return redirect(url_for('ver_blog', blog_id=blog_id))

        if 'me_gusta' in request.form:
            bd.dar_me_gusta(blog_id, session['id'])
            return redirect(url_for('ver_blog', blog_id=blog_id))
        
        usuario_actual = profesor

    return render_template('ver_blog.html', profesor=profesor, blog=blog, usuario_actual=usuario_actual, comentarios=comentarios_organizados, estadisticas=estadisticas)



@app.route('/crear_post', methods=['POST'])
@login_required
def crear_post_route():
    nombre = request.form['nombre']
    contenido = request.form['contenido']
    imagen = request.files['imagen'] if 'imagen' in request.files else None

    if imagen and allowed_file(imagen.filename):
        _, imagen_url = subir_a_gcs_por_tipo(imagen, 'blog')  
    else:
        imagen_url = 'default.png'  

    id_profesor = session.get('id')
    id_admin = 1  
    fecha_creacion = datetime.now()
    vistas = 0  

    bd.crear_post(nombre, contenido, id_profesor, id_admin, fecha_creacion, imagen_url, vistas)
    profesores = bd.obtener_todos_los_profesores() 
    for profesor in profesores:
        bd.agregar_notificacion(profesor['id'], f"Nuevo artículo publicado: {nombre}", "blog") 

    return redirect(url_for('blog'))



@app.route('/eliminar_post/<int:blog_id>', methods=['POST'])
@login_required
def eliminar_post(blog_id):
    id_profesor = session.get('id') 
    if not id_profesor:
        return redirect(url_for('login'))

    blog = bd.obtener_blog_por_id(blog_id)
    if not blog:
        return "El blog no existe", 404
    if blog['id_profesor'] != id_profesor:
        return "No tienes permiso para eliminar este blog", 403
    if blog['imagen'] and blog['imagen'].startswith("https://storage.googleapis.com/"):
        try:
            partes = blog['imagen'].split(f"{BUCKET_NAME}/")
            blob_name = partes[1] if len(partes) == 2 else f"blog/{os.path.basename(blog['imagen'])}"
            client = storage.Client()
            bucket = client.bucket(BUCKET_NAME)
            blob = bucket.blob(blob_name)
            if blob.exists():
                blob.delete()
        except Exception as e:
            print(f"Error al eliminar imagen del blog: {e}")

    bd.eliminar_blog(blog_id)
    return redirect(url_for('blog'))


@app.route('/editar_post/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def editar_post(blog_id):
    email = session.get('email')  
    id_profesor = session.get('id')  

    if not email: 
        return redirect(url_for('login'))

    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
            'apellido': "Desconocido",
            'imagen_perfil': "default.png",
            'id_profesor': None
        }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if not id_profesor:
        return redirect(url_for('login'))

    blog = bd.obtener_blog_por_id(blog_id)

    if not blog or blog['id_profesor'] != id_profesor:
        return "No tienes permiso para editar este post", 403

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        nuevo_contenido = request.form['contenido']
        nueva_imagen = request.files['imagen'] if 'imagen' in request.files else None

        if nueva_imagen and allowed_file(nueva_imagen.filename):
            imagen_url = subir_a_gcs_por_tipo(nueva_imagen, 'blog')
            bd.actualizar_blog(blog_id, nuevo_nombre, nuevo_contenido, imagen_url)
        else:
            bd.actualizar_blog(blog_id, nuevo_nombre, nuevo_contenido, blog['imagen'])

        return redirect(url_for('blog'))

    return render_template('editar_post.html', blog=blog , profesor=profesor)


def is_process_running(process_name):
    """Verifica si un proceso está en ejecución."""
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] == process_name:
            return True  
    return False



@app.route('/eliminar_comentario/<int:comentario_id>', methods=['POST'])
@login_required
def eliminar_comentario(comentario_id):
    usuario_id = session.get('id')
    comentario = bd.obtener_comentario_por_id(comentario_id)
    
    if not comentario:
        return jsonify({'error': 'Comentario no encontrado'}), 404
    
    if comentario['id_usuario'] != usuario_id:
        return jsonify({'error': 'No autorizado'}), 403

    try:
        bd.eliminar_comentario(comentario_id)
        return jsonify({'success': True, 'deleted_id': comentario_id})
    except Exception as e:
        return jsonify({'error': 'Error al eliminar el comentario'}), 500


@app.route('/denunciar_comentario/<int:comentario_id>', methods=['POST'])
@login_required
def denunciar_comentario(comentario_id):
    usuario_id = session.get('id')
    razon = request.form.get('razon', 'Contenido ofensivo')
    bd.guardar_denuncia(comentario_id, usuario_id, razon)
    return jsonify({'success': True})





@app.route('/grabacion')
@login_required
def grabacion():
    email = session.get('email')
    id_profesor = session.get('id')

    if not email:
        return redirect(url_for('login'))

    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    grabaciones = bd.obtener_grabaciones(id_usuario=id_profesor)

    return render_template('grabacion.html',
                           profesor=profesor,
                           grabaciones=grabaciones,
                           id_usuario=id_profesor)



@app.route('/guardar_audio', methods=['POST'])
def guardar_audio():
    if 'audio' not in request.files:
        return 'No se envió archivo', 400
    archivo = request.files['audio']

    id_usuario = session.get('id')
    print("ID usuario desde sesión:", id_usuario)

    if not id_usuario:
        return 'Falta ID de usuario en sesión', 400

    try:
        id_usuario = int(id_usuario)
        nombre_archivo, url_publica = subir_a_gcs_por_tipo(archivo, 'grabaciones')

        resultado = bd.guardar_grabacion(nombre_archivo, url_publica, id_usuario)

        if resultado:
            return 'Grabación guardada correctamente'
        else:
            return 'No se pudo guardar en la base de datos', 500
    except Exception as e:
        print(f"Error guardando grabación: {e}")
        traceback.print_exc()
        return 'Error al guardar en la base de datos', 500



@app.route('/eliminar_grabacion/<int:id>', methods=['POST'])
@login_required
def eliminar_grabacion(id):
    email_profesor = session.get('email') 
    connection = bd()
    cursor = connection.cursor()
    cursor.execute("SELECT email_profesor FROM grabaciones WHERE id = %s", (id,))
    grabacion = cursor.fetchone()

    if grabacion and grabacion['email_profesor'] == email_profesor:
        cursor.execute("DELETE FROM grabaciones WHERE id = %s", (id,))
        connection.commit()
        connection.close()
        return jsonify({"mensaje": "Grabación eliminada exitosamente"})
    else:
        connection.close()
        return jsonify({"mensaje": "No tienes permiso para eliminar esta grabación"}), 403



@app.route('/guitarra')
@login_required
def guitarra():
    email = session.get('email')  
    id_profesor = session.get('id')  
    
    if not email: 
        return redirect(url_for('login'))
    profesor = bd.seleccionarProfesor(email)
    if not profesor:
        profesor = {
            'nombre': "Usuario",
            'apellido': "Desconocido",
            'imagen_perfil': "default.png",
            'id_profesor': None
        }
        bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
        imagen = profesor.get('imagen_perfil') or 'default.png'
        profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    return render_template("guitarra.html", profesor=profesor)


@app.route('/notificaciones', methods=['GET'])
def obtener_notificaciones():
    id_profesor = request.args.get('id', type=int) or session.get('id')
    if not id_profesor:
        return jsonify([])  
    
    notificaciones = bd.obtener_notificaciones_db(id_profesor)
    return jsonify(notificaciones)


@app.route('/marcar_notificaciones', methods=['POST'])
def marcar_notificaciones():
    id_profesor = session.get('id')
    id_profesor = request.args.get('id')  
    bd.marcar_notificaciones_db(id_profesor)
    return jsonify({"success": True})


@app.route('/instrumentos', methods=['GET', 'POST'])  
@login_required
def instrumentos():
    email = session.get('email')  
    id_profesor = session.get('id')  
    if not email or not id_profesor: 
        return redirect(url_for('login'))
    resultado = bd.seleccionarProfesor(email)
    columnas_profesor = ['id', 'nombre', 'apellido', 'imagen_perfil', 'dni', 'direccion', 'telefono', 'mail', 'contraseña']
    profesor = dict(zip(columnas_profesor, resultado)) if resultado else None

    profesor = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = profesor.get('imagen_perfil') or 'default.png'
    profesor['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        try:
            # Validar datos del formulario
            titulo = request.form.get('titulo', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            estado = request.form.get('estado')
            imagen = request.files.get('imagen')
            
            if not all([titulo, descripcion, estado, imagen]):
                flash('Faltan campos obligatorios.')
                return redirect(request.url)

            if imagen and imagen.filename != '':
                if not allowed_file(imagen.filename):
                    flash('La imagen debe ser JPG o PNG.')
                    return redirect(request.url)
                nombre_seguro, img_url = subir_a_gcs_por_tipo(imagen, 'instrumentos')
            else:
                flash('Imagen obligatoria no enviada')
                return redirect(request.url)

            pdf = request.files.get('pdf')
            pdf_url = None
            if pdf and pdf.filename != '':
                if not allowed_file(pdf.filename):  
                    flash('Solo se permiten archivos PDF.')
                    return redirect(request.url)


                if pdf.content_length > 10 * 1024 * 1024: 
                    flash('El PDF no puede exceder 10MB.')
                    return redirect(request.url)
                nombre_pdf, pdf_url = subir_a_gcs_por_tipo(pdf, 'instrumentos')
            video_url = request.form.get('video_url', '').strip()
            bd.guardarInstrumento(
                titulo=titulo,
                descripcion=descripcion,
                imagen=img_url,  
                video_url=video_url if video_url else None,
                pdf_url=pdf_url,  
                estado=estado,
                id_profesor=id_profesor
            )

            flash('Trabajo de luthier guardado exitosamente!', 'success')
            return redirect(url_for('instrumentos'))

        except Exception as e:
            app.logger.error(f"Error al guardar instrumento: {str(e)}", exc_info=True)
            flash(f'Error al guardar: {str(e)}', 'error')
            return redirect(request.url)
    try:
        trabajos_propios = bd.obtenerInstrumentosPorProfesor(id_profesor) or []
        trabajos_publicos = bd.obtenerInstrumentosPublicosExcluyendoProfesor(id_profesor) or []

        trabajos_db = trabajos_propios + trabajos_publicos
        trabajos_luthiers = []
        
        for trabajo in trabajos_db:
            es_propio = trabajo['id_profesor'] == id_profesor
            trabajos_luthiers.append({
                'id': trabajo['id'],
                'titulo': trabajo['titulo'],
                'descripcion': trabajo['descripcion'],
                'imagen': trabajo['imagen'].replace('\\', '/'),
                'video_url': trabajo.get('video_url'),
                'pdf_url': trabajo.get('pdf_url').replace('\\', '/') if trabajo.get('pdf_url') else None,
                'es_propio': es_propio,
                'autor': profesor['nombre'] + ' ' + profesor['apellido'] if es_propio else trabajo.get('autor', 'Otro profesor')
            })
    except Exception as e:
        app.logger.error(f"Error obteniendo trabajos: {str(e)}")
        trabajos_luthiers = []
        flash('Error al cargar los trabajos', 'error')
    return render_template("instrumentos.html", 
                           profesor=profesor,
                           trabajos_luthiers=trabajos_luthiers)


@app.route('/instrumentos/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_instrumento_route(id):
    id_profesor = session.get('id')
    if not id_profesor:
        return redirect(url_for('login'))

    instrumento = bd.obtener_instrumento_por_id(id, id_profesor=id_profesor)
    if not instrumento:
        flash('Instrumento no encontrado o no autorizado', 'error')
        return redirect(url_for('instrumentos'))
    for archivo in ['imagen', 'pdf_url']:
        url = instrumento.get(archivo)
        if url and url.startswith("https://storage.googleapis.com/"):
            try:
                partes = url.split(f"{BUCKET_NAME}/")
                blob_name = partes[1] if len(partes) == 2 else f"instrumentos/{os.path.basename(url)}"
                client = storage.Client()
                bucket = client.bucket(BUCKET_NAME)
                blob = bucket.blob(blob_name)
                if blob.exists():
                    blob.delete()
            except Exception as e:
                app.logger.warning(f"Error eliminando {archivo} de GCS: {e}")

    success = bd.eliminar_instrumento(id, id_profesor=id_profesor)
    if success:
        flash('Instrumento eliminado correctamente', 'success')
    else:
        flash('No se pudo eliminar el instrumento', 'error')
    return redirect(url_for('instrumentos'))


@app.route('/instrumentos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_instrumento_route(id):
    id_profesor = session.get('id')
    if not id_profesor:
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        estado = request.form.get('estado')
        video_url = request.form.get('video_url')
        imagen = request.files.get('imagen')
        pdf = request.files.get('pdf')

        img_url = None
        pdf_url = None

        if imagen and imagen.filename:
            if not allowed_file(imagen.filename):
                flash('La imagen debe ser JPG o PNG.', 'error')
                return redirect(request.url)
            img_url = subir_a_gcs_por_tipo(imagen, 'instrumentos')

        if pdf and pdf.filename:
            if not allowed_file(pdf.filename):
                flash('Solo se permiten archivos PDF.', 'error')
                return redirect(request.url)
            if pdf.content_length > 10 * 1024 * 1024:
                flash('El PDF no puede exceder 10MB.', 'error')
                return redirect(request.url)
            pdf_url = subir_a_gcs_por_tipo(pdf, 'instrumentos')

        updated = bd.actualizar_instrumento(
            instrumento_id=id,
            titulo=titulo,
            descripcion=descripcion,
            imagen=img_url,
            video_url=video_url,
            pdf_url=pdf_url,
            estado=estado,
            id_profesor=id_profesor
        )

        if updated:
            flash('Instrumento actualizado correctamente', 'success')
            return redirect(url_for('instrumentos'))
        else:
            flash('Error al actualizar el instrumento', 'error')

    instrumento = None
    try:
        instrumentos = bd.obtenerInstrumentosPorProfesor(id_profesor)
        for ins in instrumentos:
            if ins['id'] == id:
                instrumento = ins
                break
    except Exception as e:
        flash('Error al cargar el instrumento', 'error')

    if not instrumento:
        flash('Instrumento no encontrado', 'error')
        return redirect(url_for('instrumentos'))

    return render_template('editar_instrumento.html', instrumento=instrumento)


@app.route('/admin/sync', methods=['POST'])
@login_required
def trigger_sync():
    if not session.get('es_admin'):  
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        from sync_system.sync_manager import run_sync
        success = run_sync()
        if success:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Ver logs para detalles'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

##########################
#Administración EduMusica
##########################

@app.route('/administracion')
@login_required
def administracion():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    profesorCant= bd.contar_profesores()
    blogCant = bd.contar_blog_posts()
    proyectoCant=bd.contar_proyectos()
    usuarios = bd.seleccionarUsuarios_Admin()  
    return render_template('administracion.html', administrador=administrador,
                            usuarios=usuarios,
                            profesorCant=profesorCant,
                            blogCant=blogCant,
                            proyectoCant=proyectoCant)


@app.route('/contacto_admin')
@login_required
def contacto_admin():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    mensajes = bd.obtener_mensajes_contacto()
    return render_template('admin/contacto_admin.html',administrador=administrador, mensajes=mensajes)


@app.route('/admin/contacto/responder/<int:id_contacto>', methods=['POST'])
@login_required
def responder_contacto(id_contacto):
    exito = bd.marcar_contacto_respondido(id_contacto)
    if exito:
        flash("Mensaje marcado como respondido", "success")
    else:
        flash("No se pudo actualizar el estado", "danger")

    return redirect(url_for('contacto_admin'))


@app.route('/usuarios_admin')
@login_required
def usuarios_admin():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    usuarios = bd.seleccionarUsuarios_Admin()
    admins=bd.seleccionarUsuarios_Administrador()
    
    return render_template('admin/usuarios_admin.html', administrador=administrador,
                            usuarios=usuarios,
                            admins=admins)


@app.route('/cambiar_rol/<int:id_usuario>', methods=['POST'])
@login_required
def cambiar_rol_usuario(id_usuario):
    nuevo_rol = request.form.get('rol')  
    try:
        bd.cambiar_rol(nuevo_rol, id_usuario)
        return redirect(url_for('usuarios_admin'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['mail']
        rol = request.form['rol']  
        bd.editar_usuario_admin(id, nombre, apellido, email, rol) 
        return redirect(url_for('usuarios_admin'))
    usuario = bd.obtener_usuario_por_id(id)
    return render_template('admin/editar_usuario.html', usuario=usuario, administrador=administrador)


@app.route('/eliminar_usuario/<int:id>', methods=['GET'])
@login_required
def eliminar_usuario(id):
    bd.eliminar_usuario_admin(id)
    return redirect(url_for('usuarios_admin'))

@app.route('/nuevo_usuario', methods=['GET', 'POST'])
@login_required
def nuevo_usuario():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['mail']
        password = request.form['password']  
        bd.crear_usuario_admin(nombre, apellido, email, password)
        return redirect(url_for('usuarios_admin'))
    return render_template('admin/nuevo_usuario.html', administrador=administrador)


@app.route('/editar_profesor/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_profesor(id):
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['mail']
        rol = request.form['rol']  
        bd.editar_profesor(id, nombre, apellido, email, rol)  
        return redirect(url_for('usuarios_admin'))
    profesor = bd.obtener_profesor_por_id(id)
    return render_template('admin/editar_profesor.html', profesor=profesor, administrador=administrador)


@app.route('/eliminar_profesor/<int:id>', methods=['GET'])
@login_required
def eliminar_profesor(id):
    bd.eliminar_profesor(id)
    return redirect(url_for('usuarios_admin'))

@app.route('/nuevo_profesor', methods=['GET', 'POST'])
@login_required
def nuevo_profesor():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['mail']
        password = request.form['password']
        bd.crear_profesor(nombre, email, password)
        return redirect(url_for('usuarios_admin'))
    return render_template('admin/nuevo_profesor.html', administrador=administrador)



@app.route('/blog_admin')
@login_required
def blog_admin():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    usuarios = bd.seleccionarUsuarios_Admin()
    posts = bd.seleccionarblog_Admin()
    return render_template('admin/blog_admin.html', administrador=administrador,
                            usuarios=usuarios,
                            posts=posts)


@app.route('/editar_blog/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_blog(id):
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        nombre = request.form['nombre']
        contenido = request.form['contenido']
        imagen = request.form['imagen']  

        bd.editar_blog(id, nombre, contenido, imagen)
        return redirect(url_for('blog_admin'))

    post = bd.obtener_blog_por_id(id)
    return render_template('admin/editar_blog.html', post=post, administrador=administrador)


@app.route('/nuevo_blog', methods=['GET', 'POST'])
@login_required
def nuevo_blog():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        nombre = request.form['nombre']
        contenido = request.form['contenido']
        archivo = request.files.get('imagen')

        nombre_imagen = ''
        if archivo and archivo.filename != '':
            nombre_imagen, _ = subir_a_gcs_por_tipo(archivo, 'blog')

        bd.crear_blog(nombre, contenido, nombre_imagen, id_profesor=id_profesor)
        return redirect(url_for('blog_admin'))

    return render_template('admin/nuevo_blog.html', administrador=administrador)


@app.route('/eliminar_blog/<int:id>', methods=['GET'])
@login_required
def eliminar_blog(id):
    bd.eliminar_blog(id)
    return redirect(url_for('blog_admin'))


@app.route('/recurso_admin')
@login_required
def recurso_admin():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    usuarios = bd.seleccionarUsuarios_Admin()
    recursos = bd.seleccionarRecursos_Admin()
    
    return render_template('admin/recurso_admin.html', administrador=administrador,
                            usuarios=usuarios,
                            recursos=recursos)

@app.route('/nuevo_recurso', methods=['GET', 'POST'])
@login_required
def nuevo_recurso():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']  
        archivo = request.files.get('archivo')

        nombre_archivo = ''
        if archivo and archivo.filename != '':
            nombre_archivo, _ = subir_a_gcs_por_tipo(archivo, categoria)

        bd.guardar_recurso(titulo, descripcion, nombre_archivo, categoria)
        return redirect(url_for('recurso_admin'))

    return render_template('admin/nuevo_recurso.html', administrador=administrador)


@app.route('/musica_admin')
@login_required
def musica_admin():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    usuarios = bd.seleccionarUsuarios_Admin()

    canciones = bd.seleccionarmusica_Admin()
    return render_template('admin/musica_admin.html', administrador=administrador,
                            usuarios=usuarios,
                            canciones=canciones)


@app.route('/nueva_musica', methods=['GET', 'POST'])
@login_required
def nueva_musica():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        titulo = request.form['titulo']
        artista = request.form['artista']
        album = request.form['album']
        categoria = request.form['categoria']
        archivo = request.files['archivo']

        if archivo and archivo.filename != '':
            nombre_archivo, public_url = subir_a_gcs_por_tipo(archivo, 'musica')
            bd.crear_musica(titulo, artista, album, nombre_archivo, categoria)

        return redirect(url_for('musica_admin'))

    return render_template('admin/nueva_musica.html', administrador=administrador)



@app.route('/editar_musica/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_musica(id):
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        titulo = request.form['titulo']
        artista = request.form['artista']
        categoria = request.form['categoria']
        bd.editar_musica(id, titulo, artista, categoria)
        return redirect(url_for('musica_admin'))
    
    cancion = bd.obtener_musica_por_id(id)
    return render_template('admin/editar_musica.html', cancion=cancion, administrador=administrador)


@app.route('/eliminar_musica/<int:id>')
@login_required
def eliminar_musica(id):
    bd.eliminar_musica(id)
    return redirect(url_for('musica_admin'))


@app.route('/video_admin')
@login_required
def video_admin():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    usuarios = bd.seleccionarUsuarios_Admin()
    
    videos = bd.seleccionarvideo_Admin()
    
    return render_template('admin/video_admin.html', administrador=administrador,
                            usuarios=usuarios,
                            videos=videos)

@app.route('/nuevo_video', methods=['GET', 'POST'])
@login_required
def nuevo_video():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        archivo = request.files.get('video')

        nombre_video = ''
        if archivo and archivo.filename != '':
            nombre_video, _ = subir_a_gcs_por_tipo(archivo, 'video')

        bd.guardar_video(titulo, descripcion, nombre_video)
        return redirect(url_for('video_admin'))

    return render_template('admin/nuevo_video.html', administrador=administrador)


@app.route('/proyecto_admin')
@login_required
def proyecto_admin():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
       'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    usuarios = bd.seleccionarUsuarios_Admin()
    
    proyectos= bd.seleccionarproyecto_Admin()
    
    return render_template('admin/proyecto_admin.html', administrador=administrador,
                            usuarios=usuarios,
                            proyectos=proyectos)

@app.route('/nuevo_proyecto', methods=['GET', 'POST'])
@login_required
def nuevo_proyecto():
    id_profesor = session.get('id')
    email = session.get('email')
    if not id_profesor or not email:
        return jsonify({"error": "Usuario no logueado"}), 401
    administrador = bd.seleccionarProfesor(email) or {
        'nombre': "Usuario",
        'apellido': "Desconocido",
        'imagen_perfil': "default.png",
        'id_profesor': None
    }
    bucket_url = "https://storage.googleapis.com/storage-edumusica/profile/"
    imagen = administrador.get('imagen_perfil') or 'default.png'
    administrador['imagen_url'] = imagen if imagen.startswith("http") else bucket_url + imagen

    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        archivo = request.files.get('archivo')

        nombre_archivo = ''
        if archivo and archivo.filename != '':
            nombre_archivo, _ = subir_a_gcs_por_tipo(archivo, 'proyectos')

        bd.insertar_proyecto(titulo, descripcion, nombre_archivo)
        return redirect(url_for('proyecto_admin'))

    return render_template('admin/nuevo_proyecto.html', administrador=administrador)


#@app.route('/uso-ram')
#def uso_ram():
#    process = psutil.Process(os.getpid())
#    ram_usage_mb = process.memory_info().rss / 1024 / 1024
#    return jsonify({"uso_de_ram_mb": f"{ram_usage_mb:.2f} MB"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


