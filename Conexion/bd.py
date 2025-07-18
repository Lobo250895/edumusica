import pymysql
import bcrypt
import re
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash
import pymysql.cursors
import os

def get_connection():
    try:
        return pymysql.connect(
            unix_socket=f'/cloudsql/{os.environ["INSTANCE_CONNECTION_NAME"]}', 
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"],
            db=os.environ["DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    except pymysql.MySQLError as e:
        print(f"Error de conexión a la base de datos: {e}")
        return None

# --------------------------------------------------
# Funciones para creación de tablas
# --------------------------------------------------

def crear_todas_tablas():
    """Crea todas las tablas necesarias para la aplicación"""
    crear_tabla_usuario()
    crear_tabla_admin()
    crear_tabla_proyecto()
    crear_tabla_canciones()
    crear_tabla_blog()
    crear_tabla_comentarios()
    crear_tabla_me_gusta()
    crear_tabla_notificaciones()
    crear_tabla_instrumentos()
    crear_tabla_grabaciones()
    crear_tabla_recursos()
    crear_tabla_videos()
    crear_tabla_inspiracion()
    crear_tabla_comentario_proyecto()
    crear_tabla_eventos()
    crear_tabla_mis_escuelas()
    crear_tabla_reacciones_comentarios()
    crear_tabla_reportes()
    crear_tabla_sync_control()


def crear_tabla_usuario():
    """Crea la tabla usuario"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Usuario (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL,
                    apellido VARCHAR(50) NOT NULL,
                    imagen_perfil VARCHAR(255) DEFAULT NULL,
                    dni VARCHAR(8) NOT NULL,
                    direccion VARCHAR(100) DEFAULT NULL,
                    telefono VARCHAR(15) DEFAULT NULL,
                    mail VARCHAR(100) NOT NULL UNIQUE,
                    contraseña VARCHAR(255) NOT NULL,
                    rol VARCHAR(255) NOT NULL,
                    firebase_id VARCHAR(255) NOT NULL
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla usuario: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_comentario_proyecto():
    """Crea la tabla comentario_proyecto"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comentario_proyecto (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_proyecto INT NOT NULL,
                    id_usuario INT NOT NULL,
                    comentario TEXT NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parent_id INT NULL,
                    FOREIGN KEY (id_proyecto) REFERENCES proyecto(id),
                    FOREIGN KEY (id_usuario) REFERENCES usuario(id),
                    FOREIGN KEY (parent_id) REFERENCES comentario_proyecto(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla comentario_proyecto: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_eventos():
    """Crea la tabla eventos"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS eventos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    titulo VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    fecha_inicio DATETIME NOT NULL,
                    fecha_fin DATETIME NOT NULL,
                    ubicacion VARCHAR(100),
                    id_profesor INT NOT NULL,
                    color VARCHAR(20),
                    FOREIGN KEY (id_profesor) REFERENCES usuario(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla eventos: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_mis_escuelas():
    """Crea la tabla mis_escuelas"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mis_escuelas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    direccion VARCHAR(200),
                    telefono VARCHAR(20),
                    id_profesor INT NOT NULL,
                    FOREIGN KEY (id_profesor) REFERENCES usuario(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla mis_escuelas: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_reacciones_comentarios():
    """Crea la tabla reacciones_comentarios"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reacciones_comentarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_comentario INT NOT NULL,
                    id_usuario INT NOT NULL,
                    tipo_reaccion ENUM('like', 'dislike') NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_comentario) REFERENCES comentarios(id),
                    FOREIGN KEY (id_usuario) REFERENCES usuario(id),
                    UNIQUE KEY (id_comentario, id_usuario)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla reacciones_comentarios: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_reportes():
    """Crea la tabla reportes"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reportes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario_reportador INT NOT NULL,
                    id_contenido INT NOT NULL,
                    tipo_contenido ENUM('blog', 'comentario', 'proyecto', 'video') NOT NULL,
                    motivo TEXT NOT NULL,
                    estado ENUM('pendiente', 'resuelto', 'rechazado') DEFAULT 'pendiente',
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_usuario_reportador) REFERENCES usuario(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla reportes: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_sync_control():
    """Crea la tabla sync_control"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_control (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tabla VARCHAR(50) NOT NULL,
                    ultima_sincronizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado VARCHAR(20) NOT NULL
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla sync_control: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_admin():
    """Crea la tabla admin"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL,
                    apellido VARCHAR(50) NOT NULL,
                    dni VARCHAR(8) NOT NULL,
                    contraseña VARCHAR(255) NOT NULL,
                    mail VARCHAR(50) NOT NULL UNIQUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla admin: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_proyecto():
    """Crea la tabla proyecto"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proyecto (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    autor VARCHAR(100) NOT NULL,
                    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    proyecto VARCHAR(255) NOT NULL,
                    estado VARCHAR(50) NOT NULL,
                    es_publico BOOLEAN DEFAULT FALSE,
                    autor_id INT,
                    FOREIGN KEY (autor_id) REFERENCES usuario(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla proyecto: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_canciones():
    """Crea la tabla canciones"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS canciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    titulo VARCHAR(50) NOT NULL,
                    artist VARCHAR(50),
                    album VARCHAR(50),
                    ruta_archivo VARCHAR(100) NOT NULL,
                    categoria VARCHAR(50)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla canciones: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_blog():
    """Crea la tabla blog"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blog (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL,
                    contenido TEXT NOT NULL,
                    id_profesor INT NOT NULL,
                    id_admin INT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    imagen VARCHAR(100) NOT NULL,
                    vistas INT DEFAULT 0,
                    FOREIGN KEY (id_profesor) REFERENCES usuario(id),
                    FOREIGN KEY (id_admin) REFERENCES admin(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla blog: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_comentarios():
    """Crea la tabla comentarios"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comentarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_blog INT NOT NULL,
                    id_usuario INT NOT NULL,
                    comentario TEXT NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parent_id INT NULL,
                    FOREIGN KEY (id_blog) REFERENCES blog(id),
                    FOREIGN KEY (id_usuario) REFERENCES usuario(id),
                    FOREIGN KEY (parent_id) REFERENCES comentarios(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla comentarios: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_me_gusta():
    """Crea la tabla me_gusta"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS me_gusta (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_blog INT NOT NULL,
                    id_usuario INT NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_blog) REFERENCES blog(id),
                    FOREIGN KEY (id_usuario) REFERENCES usuario(id),
                    UNIQUE KEY (id_blog, id_usuario)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla me_gusta: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_notificaciones():
    """Crea la tabla notificaciones"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notificaciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    mensaje TEXT NOT NULL,
                    tipo ENUM('blog','material','cancion','video') NOT NULL,
                    visto BOOLEAN DEFAULT FALSE,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla notificaciones: {e}")
    finally:
        if connection:
            connection.close()


def crear_tabla_instrumentos():
    """Crea la tabla instrumentos"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS instrumentos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    titulo VARCHAR(255) NOT NULL,
                    descripcion TEXT,
                    imagen VARCHAR(255),
                    video_url VARCHAR(255),
                    pdf_url VARCHAR(255),
                    id_profesor INT,
                    estado ENUM('publico','privado') DEFAULT 'privado',
                    FOREIGN KEY (id_profesor) REFERENCES usuario(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla instrumentos: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_grabaciones():
    """Crea la tabla grabaciones"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS grabaciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255),
                    ruta VARCHAR(255),
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                    email_profesor VARCHAR(255)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla grabaciones: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_recursos():
    """Crea la tabla recursos"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recursos (
                    id VARCHAR(36) PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    url TEXT NOT NULL,
                    categoria ENUM('libros','peliculas','web') NOT NULL,
                    tamanio VARCHAR(50),
                    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla recursos: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_videos():
    """Crea la tabla videos"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS video (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL,
                    ruta_archivo VARCHAR(100) NOT NULL,
                    genero VARCHAR(50) NOT NULL,
                    imagen VARCHAR(50) NOT NULL,
                    id_profesor INT NOT NULL,
                    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_profesor) REFERENCES usuario(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla video: {e}")
    finally:
        if connection:
            connection.close()

def crear_tabla_inspiracion():
    """Crea la tabla inspiracion"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inspiracion (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL,
                    ruta_archivo VARCHAR(100) NOT NULL,
                    tipo_archivo VARCHAR(50) NOT NULL,
                    id_profesor INT NOT NULL,
                    FOREIGN KEY (id_profesor) REFERENCES usuario(id)
                )
            ''')
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear tabla inspiracion: {e}")
    finally:
        if connection:
            connection.close()


# --------------------------------------------------
# Funciones principales
# --------------------------------------------------

def actualizar_firebase_id_profesor(email, firebase_id):
    """Actualiza el campo firebase_id de un profesor"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET firebase_id = %s WHERE mail = %s",
            (firebase_id, email)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar firebase_id: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()


def validar_email(email):
    """Verifica que el email sea válido."""
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validar_telefono(telefono):
    """Verifica que el teléfono sea válido (solo números)."""
    return telefono.isdigit() and len(telefono) in range(10, 16)



def registrarUsuario(nombre, apellido, dni, direccion, telefono, email, hashed_password, firebase_id):
    """Registra un nuevo usuario en la base de datos."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(''' 
                INSERT INTO usuario 
                (nombre, apellido, dni, direccion, telefono, mail, contraseña, firebase_id, rol)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'profesor')
            ''', (nombre, apellido, dni, direccion, telefono, email, hashed_password, firebase_id))
            connection.commit()
            return True
    except pymysql.MySQLError as e:
        print(f"Error al registrar el usuario: {e}")
        return False
    finally:
        if connection:
            connection.close()


def Login_profesor(email, contraseña):
    """Verifica las credenciales del profesor para el login y devuelve una tupla (id, rol) si es válido."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(''' 
                SELECT id, mail, contraseña, rol FROM usuario WHERE mail = %s
            ''', (email,))
            resultado = cursor.fetchone()
            
            if resultado and bcrypt.checkpw(contraseña.encode('utf-8'), resultado['contraseña'].encode('utf-8')):
                return resultado['id'], resultado['rol']  
            return False
    except pymysql.MySQLError as e:
        print(f"Error al intentar iniciar sesión: {e}")
        return False
    finally:
        connection.close()


def seleccionarProfesor(email):
    """Obtiene los datos de un profesor por su email."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(''' 
                SELECT * FROM usuario WHERE mail = %s
            ''', (email,))
            resultado = cursor.fetchone()
            return resultado
    except pymysql.MySQLError as e:
        print(f"Error al consultar los datos del profesor: {e}")
        return None
    finally:
        connection.close()

def obtener_todos_los_profesores():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM usuario") 
    profesores = cursor.fetchall()
    connection.close()
    return profesores


def eliminar_usuario(usuario_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM usuario WHERE id = %s", (usuario_id,))
        connection.commit()
    finally:
        connection.close()



def actualizar_datos_en_bd(nombre, apellido, dni, direccion, telefono, mail):
    try:
        connection = get_connection()  
        with connection.cursor() as cursor:
            print(f"Actualizando datos para el correo: {mail}")  
            cursor.execute(''' 
                UPDATE usuario
                SET nombre = %s, apellido = %s, dni = %s, direccion = %s, telefono = %s
                WHERE mail = %s
            ''', (nombre, apellido, dni, direccion, telefono, mail))
            connection.commit()
            if cursor.rowcount > 0:
                print("Datos actualizados correctamente.")
            else:
                print("No se actualizó ningún dato. Verifica el correo en la base de datos.")
    except pymysql.MySQLError as e:
        print(f"Error al actualizar el perfil: {e}")
    finally:
        connection.close()



def actualizar_datos_profesor(email_actual, nombre, apellido, dni, direccion, telefono, nuevo_email, nueva_contraseña):
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                if nueva_contraseña:  # Solo si el usuario ingresó nueva contraseña
                    hashed_password = bcrypt.hashpw(nueva_contraseña.encode('utf-8'), bcrypt.gensalt())
                    sql = """
                        UPDATE usuario
                        SET nombre = %s,
                            apellido = %s,
                            dni = %s,
                            direccion = %s,
                            telefono = %s,
                            mail = %s,
                            contraseña = %s
                        WHERE mail = %s
                    """
                    cursor.execute(sql, (nombre, apellido, dni, direccion, telefono, nuevo_email, hashed_password, email_actual))
                else:  # Si no ingresó nueva contraseña, no la tocamos
                    sql = """
                        UPDATE usuario
                        SET nombre = %s,
                            apellido = %s,
                            dni = %s,
                            direccion = %s,
                            telefono = %s,
                            mail = %s
                        WHERE mail = %s
                    """
                    cursor.execute(sql, (nombre, apellido, dni, direccion, telefono, nuevo_email, email_actual))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error actualizando datos personales: {e}")
        finally:
            conn.close()
    return False


def obtener_imagen(mail):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT imagen_perfil FROM usuario WHERE mail = %s', (mail,))
            imagen = cursor.fetchone()
            return imagen[0] if imagen else None
    except pymysql.MySQLError as e:
        print(f"Error al obtener la imagen: {e}")
        return None
    finally:
        connection.close()


def actualizar_imagen_en_bd(email, ruta_imagen):
    try:
        connection = get_connection()
        if connection is None:
            print("Error: No se pudo conectar a la base de datos")
            return False
            
        print(f"Intentando actualizar imagen. Email: {email}, Ruta: {ruta_imagen}")  # Debug
            
        with connection.cursor() as cursor:
            cursor.execute('''
                UPDATE usuario
                SET imagen_perfil = %s
                WHERE mail = %s
            ''', (ruta_imagen, email))
            
            rows_affected = cursor.rowcount
            connection.commit()
            
            print(f"Filas afectadas: {rows_affected}")  # Debug
            
            if rows_affected > 0:
                print(f"Imagen actualizada correctamente para {email}")
                return True
            else:
                print(f"No se encontró usuario con email {email}")
                return False
                
    except pymysql.MySQLError as e:
        print(f"Error al actualizar la imagen: {e}")
        return False
    finally:
        if connection:
            connection.close()

def obtener_nombre_profesor(email):
    """Obtiene el nombre de un profesor por su email."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = "SELECT nombre FROM usuario WHERE mail = %s;"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            return result['nombre'] if result else None
    except pymysql.MySQLError as e:
        print(f"Error al obtener el nombre del profesor: {e}")
        return None
    finally:
        connection.close()

def obtener_datos_profesor(email):
    """Obtiene los datos (nombre, apellido, imagen_perfil) del profesor a partir del email."""
    try:
        query = "SELECT nombre, apellido, imagen_perfil FROM usuario WHERE mail = %s;"  
        cursor = get_connection().cursor()
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result['nombre'], result['apellido'], result['imagen_perfil']
        return None, None, None
    except Exception as e:
        print(f"Error al obtener los datos del profesor: {e}")
        return None, None, None


def seleccionar_usuario_por_id(id_usuario):
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM usuario WHERE id = %s", (id_usuario,))
            return cursor.fetchone()
    except pymysql.MySQLError as e:
        print(f"Error al obtener usuario: {e}")
        return None
    finally:
        connection.close()


def guardar_contacto(nombre, email, asunto, mensaje):
    try:
        conn = get_connection()
        if conn is None:
            return False
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO contacto (nombre, email, asunto, mensaje)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, email, asunto, mensaje))
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] al guardar contacto: {e}")
        return False
    finally:
        if conn:
            conn.close()

def obtener_mensajes_contacto():
    try:
        conn = get_connection()
        if conn is None:
            return []
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM contacto ORDER BY fecha_envio DESC")
            return cursor.fetchall()
    except Exception as e:
        print(f"[ERROR] al obtener mensajes: {e}")
        return []
    finally:
        if conn:
            conn.close()

def marcar_contacto_respondido(id_contacto):
    try:
        conn = get_connection()
        if conn is None:
            return False
        with conn.cursor() as cursor:
            sql = "UPDATE contacto SET respondido = TRUE WHERE id = %s"
            cursor.execute(sql, (id_contacto,))
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] al marcar respondido: {e}")
        return False
    finally:
        if conn:
            conn.close()





# --------------------------------------------------
# Funciones para canciones y playlists
# --------------------------------------------------

def obtener_canciones():
    """Obtiene todas las canciones registradas."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM canciones;")
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error al obtener canciones: {e}")
        return []
    finally:
        connection.close()


def obtener_canciones_por_genero(genero):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = "SELECT * FROM canciones WHERE categoria = %s"
            cursor.execute(query, (genero,))
            canciones = cursor.fetchall()
            return canciones
    except pymysql.MySQLError as e:
        print(f"Error al obtener canciones por género: {e}")
        return []
    finally:
        connection.close()

def obtener_conteo_canciones_por_genero():
    """Obtiene el conteo de canciones por cada género"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT categoria, COUNT(*) as total_canciones 
                FROM canciones 
                GROUP BY categoria
            """)
            return {row['categoria']: row['total_canciones'] for row in cursor.fetchall()}
    except pymysql.MySQLError as e:
        print(f"Error al obtener conteo de canciones por género: {e}")
        return {}
    finally:
        connection.close()

def agregar_playlist( playlist_name, profesor_id):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            # Verificar si el id_profesor existe en la tabla profesor
            cursor.execute("SELECT id FROM usuario WHERE id = %s;", (profesor_id,))
            if cursor.fetchone() is None:
                raise ValueError("El profesor con id no existe.")
            
            # Insertar la playlist
            cursor.execute("INSERT INTO playlists (nombre, id_profesor) VALUES (%s, %s);", (playlist_name, profesor_id))
            connection.commit()
            return cursor.lastrowid  # Retorna el ID de la nueva playlist
    except pymysql.MySQLError as e:
        print(f"Error al agregar la playlist: {e}")
        raise
    except ValueError as e:
        print(f"Error de validación: {e}")
        raise
    finally:
        connection.close()


def agregar_canciones_a_playlist(playlist_id, canciones_seleccionadas):
    try:
        connection = get_connection()  # Obtener la conexión
        with connection.cursor() as cursor:  # Usar el cursor dentro de la conexión
            for cancion_id in canciones_seleccionadas:
                cursor.execute("INSERT INTO playlist_canciones (playlist_id, cancion_id) VALUES (%s, %s);", (playlist_id, cancion_id))
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al agregar canciones a la playlist: {e}")
        raise
    finally:
        connection.close()  

def obtener_playlists(id_profesor):
    """Devuelve las playlists creadas por un profesor."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT id, nombre
                FROM playlists
                WHERE id_profesor = %s
            ''', (id_profesor,))
            return cursor.fetchall()  
    except pymysql.MySQLError as e:
        print(f"Error al obtener playlists: {e}")
        return []
    finally:
        connection.close()




def obtener_canciones_playlist(id_playlist):
    """Obtiene las canciones de una playlist."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT c.id, c.titulo, c.artista, c.ruta_archivo
                FROM canciones c
                INNER JOIN playlist_canciones pc ON c.id = pc.cancion_id
                WHERE pc.playlist_id = %s
            ''', (id_playlist,))
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error al obtener canciones de la playlist: {e}")
        return []
    finally:
        if connection:
            connection.close()


def obtener_canciones_por_playlist(id_playlist):
    """Obtiene las canciones de una playlist desde la base de datos."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT c.id, c.titulo, c.artista, c.ruta_archivo
                FROM canciones c
                JOIN playlist_canciones pc ON c.id = pc.cancion_id
                WHERE pc.playlist_id = %s
            ''', (id_playlist,))
            canciones = cursor.fetchall()  
            return canciones
    except pymysql.MySQLError as e:
        print(f"Error al obtener canciones de la playlist: {e}")
        return []
    finally:
        connection.close()


def insertar_cancion(titulo, artista, album, ruta_archivo, categoria):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(''' 
                INSERT INTO canciones (titulo, artista, album, ruta_archivo, categoria)
                VALUES (%s, %s, %s, %s, %s)
            ''', (titulo, artista, album, ruta_archivo, categoria))
            connection.commit()
            
            return True
    except pymysql.MySQLError as e:
        print(f"Error al registrar la cancion compartida: {e}")
        return False
    finally:
        connection.close()

def obtener_canciones_publicas():
    """Obtiene canciones públicas de la tabla inspiracion"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT id, nombre, ruta_archivo, 
                       'Desconocido' as artista, 
                       'Varios' as album,
                       'compartido' as categoria
                FROM inspiracion
                WHERE estado = 1 AND tipo_archivo = 'mp3'
            ''')
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error al obtener canciones públicas: {e}")
        return []
    finally:
        if connection:
            connection.close()

def obtener_archivo_por_id(id_archivo):
    """Obtiene un archivo de inspiracion por su ID"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT id, nombre, ruta_archivo, tipo_archivo, estado
                FROM inspiracion
                WHERE id = %s
            ''', (id_archivo,))
            return cursor.fetchone()
    except pymysql.MySQLError as e:
        print(f"Error al obtener archivo: {e}")
        return None
    finally:
        if connection:
            connection.close()

def eliminar_cancion_por_ruta(ruta_archivo):
    """Elimina una canción por su ruta de archivo"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                DELETE FROM canciones
                WHERE ruta_archivo = %s AND categoria = 'compartido'
            ''', (ruta_archivo,))
            connection.commit()
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al eliminar canción: {e}")
        return False
    finally:
        if connection:
            connection.close()

# --------------------------------------------------
# Funciones para proyectos
# --------------------------------------------------

def insertar_proyecto(nombre, autor, fecha_subida, proyecto, estado, es_publico, autor_id):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = """
            INSERT INTO proyecto (nombre, autor, fecha_subida, proyecto, estado, es_publico, autor_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (nombre, autor, fecha_subida, proyecto, estado, es_publico, autor_id))
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al insertar proyecto: {e}")
    finally:
        connection.close()

def eliminar_proyecto(proyecto_id, autor_id):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            # Verificar primero que el proyecto pertenece al autor
            cursor.execute('''
                SELECT id FROM proyecto 
                WHERE id = %s AND autor_id = %s
            ''', (proyecto_id, autor_id))
            
            if not cursor.fetchone():
                return False  # El proyecto no existe o no pertenece al usuario
            
            # Si la verificación pasa, proceder a eliminar
            cursor.execute('''
                DELETE FROM proyecto
                WHERE id = %s AND autor_id = %s
            ''', (proyecto_id, autor_id))
            
            connection.commit()
            return cursor.rowcount > 0
            
    except pymysql.MySQLError as e:
        print(f"Error al eliminar proyecto ID {proyecto_id}: {e}")
        connection.rollback()
        return False
    finally:
        if connection:
            connection.close()

def obtener_detalles_proyecto(id):
    try:
        connection = get_connection()
        print("Conexión a la base de datos establecida")
        with connection.cursor() as cursor:
            query = """
            SELECT p.id, p.nombre, p.fecha_subida, p.proyecto, p.estado, p.es_publico, 
                   p.proyecto, prof.id AS autor_id, prof.nombre AS autor
            FROM proyecto p
            JOIN usuario prof ON p.autor_id = prof.id
            WHERE p.id = %s
            """
            cursor.execute(query, (id,))
            proyecto = cursor.fetchone()
            print(f"Detalles del proyecto recuperados: {proyecto}")
            return proyecto
    except pymysql.MySQLError as e:
        print(f"Error al obtener el proyecto: {e}")
        return None
    finally:
        connection.close()


def obtener_proyectos_por_profesor(id):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = """
            SELECT p.id, p.nombre, p.fecha_subida, p.estado, p.es_publico
            FROM proyecto p
            WHERE p.autor_id = %s
            """
            cursor.execute(query, (id,))
            proyectos = cursor.fetchall()
            return proyectos
    except pymysql.MySQLError as e:
        print(f"Error al obtener proyectos: {e}")
        return []
    finally:
        connection.close()

def obtener_proyecto_por_id(proyecto_id):
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM proyecto WHERE id = %s', (proyecto_id,))
            return cursor.fetchone()
    except pymysql.MySQLError as e:
        print(f"Error al obtener proyecto: {e}")
        return None
    finally:
        if connection:
            connection.close()


def obtener_proyectos_del_administrador():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = """
                SELECT id, nombre, fecha_subida, proyecto, estado, es_publico 
                FROM proyecto 
                WHERE autor_id = %s
            """
            cursor.execute(query, (2,))
            proyectos = cursor.fetchall()
            return proyectos
    except pymysql.MySQLError as e:
        print(f"Error al obtener proyectos del administrador: {e}")
        return []
    finally:
        connection.close()



def obtener_todos_los_proyectos():
    """Obtiene todos los proyectos registrados con los campos necesarios."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = """
                SELECT id, nombre, autor, fecha_subida, proyecto, estado, es_publico, autor_id
                FROM proyecto;
            """
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error al obtener proyectos: {e}")
        return []
    finally:
        connection.close()

def insertar_comentario(proyecto_id, usuario_id, contenido, comentario_padre_id=None):
    """
    Inserta un nuevo comentario en la base de datos
    
    Args:
        proyecto_id (int): ID del proyecto al que pertenece el comentario
        usuario_id (int): ID del usuario que realiza el comentario
        contenido (str): Texto del comentario
        comentario_padre_id (int, optional): ID del comentario padre si es una respuesta. Defaults to None.
    
    Returns:
        int: ID del comentario insertado o None si hubo error
    """
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            # Consulta mejorada para autoincrementar el ID
            query = """
            INSERT INTO comentario_proyecto 
                (proyecto_id, usuario_id, contenido, fecha_creacion, comentario_padre_id)
            VALUES 
                (%s, %s, %s, NOW(), %s);
            """
            
            # Ejecutamos la consulta
            cursor.execute(query, (proyecto_id, usuario_id, contenido, comentario_padre_id))
            
            # Obtenemos el ID generado automáticamente
            nuevo_id = cursor.lastrowid
            
            connection.commit()
            return nuevo_id
            
    except pymysql.MySQLError as e:
        print(f"Error al insertar comentario: {e}")
        # Podrías también loggear este error en un sistema de logging
        return None
        
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None
        
    finally:
        if connection:
            connection.close()

def obtener_comentarios_por_proyecto(proyecto_id):
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT c.id, c.contenido, c.fecha_creacion, c.comentario_padre_id,
                   u.nombre AS autor_nombre, u.imagen_perfil
            FROM comentario_proyecto c
            JOIN usuario u ON u.id = c.usuario_id
            WHERE c.proyecto_id = %s
            ORDER BY c.fecha_creacion ASC;
            """
            cursor.execute(query, (proyecto_id,))
            return cursor.fetchall()
    finally:
        if connection:
            connection.close()



# En tu módulo de base de datos (bd.py)
def obtener_comentarios_proyecto(proyecto_id):
    connection = get_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT 
                c.id, 
                c.contenido, 
                c.fecha_creacion,
                c.comentario_padre_id,
                u.nombre as nombre_autor,
                u.imagen_perfil as avatar_autor
            FROM comentario_proyecto c
            JOIN usuario u ON c.usuario_id = u.id
            WHERE c.proyecto_id = %s
            ORDER BY c.fecha_creacion ASC
            """
            cursor.execute(query, (proyecto_id,))
            resultados = cursor.fetchall()
            
            return resultados
    finally:
        if connection:
            connection.close()

def estructurar_comentarios_en_arbol(comentarios):
    comentario_dict = {c['id']: {**c, 'respuestas': []} for c in comentarios}
    arbol = []

    for comentario in comentarios:
        padre_id = comentario.get('comentario_padre_id')
        if padre_id:
            comentario_dict[padre_id]['respuestas'].append(comentario_dict[comentario['id']])
        else:
            arbol.append(comentario_dict[comentario['id']])
    
    return arbol


# --------------------------------------------------
# Funciones para mi inspiracion
# --------------------------------------------------
def obtener_archivos_profesor(id_profesor):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT `id`, `nombre`, `ruta_archivo`, `tipo_archivo`, `id_de_profesor`, `estado`
                FROM inspiracion
                WHERE id_de_profesor = %s
            ''', (id_profesor,))
            return cursor.fetchall()  
    except pymysql.MySQLError as e:
        print(f"Error al obtener los archivos: {e}")
        return []
    finally:
        if connection:
            connection.close()

def insertar_archivos_profesor(id_profesor, nombre, ruta_archivo, tipo_archivo, estado):
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO inspiracion (nombre, ruta_archivo, tipo_archivo, id_de_profesor, estado)
                VALUES (%s, %s, %s, %s, %s)
            ''', (nombre, ruta_archivo, tipo_archivo, id_profesor, estado))
            connection.commit()
        print("Archivo insertado exitosamente.")
        return True
    except pymysql.MySQLError as e:
        print(f"Error al insertar los archivos: {e}")
        return False
    finally:
        if connection:
            connection.close()


def eliminar_archivo_inspiracion(archivo_id, id_profesor):
    """Elimina un archivo de inspiracion"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                DELETE FROM inspiracion
                WHERE id = %s AND id_de_profesor = %s
            ''', (archivo_id, id_profesor))
            connection.commit()
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al eliminar archivo de inspiracion: {e}")
        return False
    finally:
        if connection:
            connection.close()

def actualizar_estado_archivo(id_archivo, nuevo_estado):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                UPDATE inspiracion SET estado = %s WHERE id = %s
            ''', (nuevo_estado, id_archivo))
            connection.commit()
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al editar archivo de inspiracion: {e}")
        return False
    finally:
        if connection:
            connection.close()


# --------------------------------------------------
# Funciones para blog y comentarios
# --------------------------------------------------

def obtener_blog():
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:  # Usa DictCursor
            cursor.execute('''
                SELECT id, nombre, contenido, id_profesor, id_admin, fecha_creacion,imagen
                FROM blog
            ''')
            blogs = cursor.fetchall()
            #print("Blogs obtenidos:", blogs)  # Depuración
            return blogs  
    except pymysql.MySQLError as e:
        print(f"Error al obtener los blogs: {e}")
        return []
    finally:
        connection.close()

def obtener_blog_por_id(blog_id):
    """ Obtiene un blog específico por su ID """
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM blog WHERE id = %s", (blog_id,))
            return cursor.fetchone()
    except pymysql.MySQLError as e:
        print(f"Error al obtener el blog: {e}")
        return None
    finally:
        connection.close()

def obtener_comentarios(blog_id):
    """ Obtiene todos los comentarios de un blog por su ID """
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT c.id, c.id_blog, c.id_usuario, c.comentario, c.fecha, 
                       p.nombre, p.apellido 
                FROM comentarios c
                JOIN usuario p ON c.id_usuario = p.id
                WHERE c.id_blog = %s
                ORDER BY c.fecha DESC;
            """, (blog_id,))
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error al obtener comentarios: {e}")
        return []
    finally:
        connection.close()


def agregar_comentario(blog_id, id_usuario, comentario, parent_id=None):
    """ Agrega un comentario a un blog """
    try:
        if parent_id in ('', None):
            parent_id = None  # Asegurarse de que sea None para que MySQL lo acepte

        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO comentarios (id_blog, id_usuario, comentario, parent_id) VALUES (%s, %s, %s, %s)",
                (blog_id, id_usuario, comentario, parent_id)
            )
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al insertar comentario: {e}")
    finally:
        connection.close()


def crear_post(nombre, contenido, id_profesor, id_admin, fecha_creacion, imagen, vistas):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO blog (nombre, contenido, id_profesor, id_admin, fecha_creacion, imagen, vistas) VALUES (%s, %s, %s,  %s,%s, %s, %s)", 
                        (nombre, contenido, id_profesor, id_admin, fecha_creacion, imagen, vistas))
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al insertar el blog: {e}")
    finally:
        connection.close()



def eliminar_blog(blog_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM blog WHERE id = %s", (blog_id,))
    connection.commit()
    connection.close()

def actualizar_blog(blog_id, nuevo_nombre, nuevo_contenido, nueva_imagen):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE blog
            SET nombre = %s, contenido = %s, imagen = %s 
            WHERE id = %s
        """, (nuevo_nombre, nuevo_contenido, nueva_imagen, blog_id))
    connection.commit()
    connection.close()


def obtener_estadisticas(blog_id):
    """ Obtiene la cantidad de likes, comentarios y vistas de un post """
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM me_gusta WHERE id_blog = %s) AS likes,
                    (SELECT COUNT(*) FROM comentarios WHERE id_blog = %s) AS comentarios,
                    vistas
                FROM blog
                WHERE id = %s
            """, (blog_id, blog_id, blog_id))
            return cursor.fetchone()
    except pymysql.MySQLError as e:
        print(f"Error al obtener estadísticas: {e}")
        return {"likes": 0, "comentarios": 0, "vistas": 0}
    finally:
        connection.close()

def incrementar_vistas(blog_id):
    """ Aumenta en 1 la cantidad de vistas de un blog """
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE blog SET vistas = vistas + 1 WHERE id = %s", (blog_id,))
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al incrementar vistas: {e}")
    finally:
        connection.close()


def dar_me_gusta(blog_id, id_usuario):
    """ Agrega un 'Me gusta' si el usuario no lo ha dado antes """
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO me_gusta (id_blog, id_usuario) VALUES (%s, %s)", (blog_id, id_usuario))
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al dar Me gusta: {e}")
    finally:
        connection.close()


def eliminar_comentario(comentario_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM comentarios WHERE parent_id = %s", (comentario_id,))

            cursor.execute("DELETE FROM comentarios WHERE id = %s", (comentario_id,))
        connection.commit()
    finally:
        connection.close()

def guardar_denuncia(comentario_id, usuario_id, razon):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar si ya existe una denuncia
            cursor.execute("""
                SELECT COUNT(*) FROM denuncias_comentarios
                WHERE comentario_id = %s AND usuario_id = %s
            """, (comentario_id, usuario_id))
            
            resultado = cursor.fetchone()
            if resultado[0] > 0:
                # Ya fue denunciado por este usuario
                print("Ya existe una denuncia de este usuario.")
                return False

            # Insertar nueva denuncia
            sql = """
                INSERT INTO denuncias_comentarios (comentario_id, usuario_id, razon)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (comentario_id, usuario_id, razon))
        connection.commit()
        return True
    finally:
        connection.close()

def obtener_comentario_por_id(comentario_id):
    connection = get_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM comentarios WHERE id = %s", (comentario_id,))
            return cursor.fetchone()
    finally:
        connection.close()


# --------------------------------------------------
# Funciones para recursos
# --------------------------------------------------

def obtener_recursos():
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:  
            cursor.execute('''
                SELECT id, nombre, url, categoria
                FROM recursos
            ''')
            recursos = cursor.fetchall()
            print("recursos obtenidos:", recursos)  # Depuración
            return recursos  
    except pymysql.MySQLError as e:
        print(f"Error al obtener los recursos: {e}")
        return []
    finally:
        connection.close()


def guardar_recurso(nombre, url, categoria, tamanio=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO recursos (nombre, url, categoria, tamanio)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, url, categoria, tamanio))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error al guardar recurso: {e}")
        return False

def obtener_recursos_por_categoria(categoria):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM recursos WHERE categoria = %s ORDER BY nombre", (categoria,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener recursos: {e}")
        return []



# --------------------------------------------------
# Funciones para notificaciones
# --------------------------------------------------


def obtener_notificaciones_db(id_profesor):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM notificaciones WHERE usuario_id = %s AND visto = FALSE ORDER BY fecha DESC", (id_profesor,))
    notificaciones = cursor.fetchall()
    connection.close()
    return notificaciones

def marcar_notificaciones_db(id_profesor):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE notificaciones SET visto = TRUE WHERE usuario_id = %s", (id_profesor,))
    connection.commit()
    connection.close()

def agregar_notificacion(id_profesor, mensaje, tipo):
    print(f"Agregando notificación para {id_profesor}: {mensaje} - {tipo}")
    connection = get_connection()
    cursor = connection.cursor()
    sql = "INSERT INTO notificaciones (usuario_id, mensaje, tipo, visto, fecha) VALUES (%s, %s, %s, %s, %s)"
    valores = (id_profesor, mensaje, tipo, False, datetime.now())
    cursor.execute(sql, valores)
    connection.commit()
    cursor.close()
    connection.close()


# --------------------------------------------------
# Funciones para videos
# --------------------------------------------------

def ver_videos():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT `id`, `nombre`, `ruta_archivo`, `genero`, `imagen`, `profesor_id`, `fecha_subida` FROM video")
    videos = cursor.fetchall() 
    #print(videos) 
    connection.close()
    return videos  

def guardar_video(nombre, ruta_archivo, genero, imagen, profesor_id):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            # Consulta SQL actualizada con profesor_id
            sql = """
                INSERT INTO video (nombre, ruta_archivo, genero, imagen, profesor_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, ruta_archivo, genero, imagen, profesor_id))
            connection.commit()
            return True
    except Exception as e:
        print(f"Error al guardar el video: {e}")
        return False
    finally:
        if connection:
            connection.close()



# --------------------------------------------------
# Funciones para grabaciones
# --------------------------------------------------

def obtener_grabaciones(id_usuario=None):
    connection = get_connection()
    cursor = connection.cursor()

    if id_usuario:
        cursor.execute("SELECT * FROM grabaciones WHERE id_usuario = %s", (id_usuario,))
    else:
        cursor.execute("SELECT * FROM grabaciones")

    grabaciones = cursor.fetchall()
    connection.close()
    return grabaciones

import traceback

def guardar_grabacion(nombre, ruta, id_usuario=None):
    """Guarda una grabación en la base de datos"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            id_usuario = int(id_usuario) if id_usuario is not None else None

            # Mostrar los datos antes de insertar
            print("Intentando guardar grabación con valores:")
            print(f"Nombre: {nombre}, Ruta: {ruta}, ID Usuario: {id_usuario}")

            cursor.execute('''
                INSERT INTO grabaciones (nombre, ruta, fecha, id_usuario)
                VALUES (%s, %s, NOW(), %s)
            ''', (nombre, ruta, id_usuario))

            connection.commit()

            # Verificar si se insertó correctamente
            if cursor.rowcount == 1:
                print("✅ Grabación guardada correctamente en la base de datos.")
                return cursor.lastrowid
            else:
                print("⚠️ No se insertó ninguna fila.")
                return None

    except Exception as e:
        print(f"❌ Error al guardar grabación: {e}")
        traceback.print_exc()
        return None
    finally:
        if connection:
            connection.close()



def eliminar_grabacion(grabacion_id, id_usuario=None):
    """Elimina una grabación"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            if id_usuario:
                cursor.execute('''
                    DELETE FROM grabaciones
                    WHERE id = %s AND id_usuario = %s
                ''', (grabacion_id, id_usuario))
            else:
                cursor.execute('''
                    DELETE FROM grabaciones
                    WHERE id = %s
                ''', (grabacion_id,))
            connection.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al eliminar grabación: {e}")
        return False
    finally:
        if connection:
            connection.close()



# --------------------------------------------------
# Funciones para creación de instrumentos
# --------------------------------------------------


def guardarInstrumento(titulo, descripcion, imagen, video_url, pdf_url, estado, id_profesor):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO instrumentos 
            (titulo, descripcion, imagen, video_url, pdf_url, estado, id_profesor)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (titulo, descripcion, imagen, video_url, pdf_url, estado, id_profesor))
        
        connection.commit()
        return cursor.lastrowid 
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


def obtenerInstrumentosPorProfesor(id_profesor):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT id, titulo, descripcion, imagen, video_url, pdf_url, estado,id_profesor
            FROM instrumentos 
            WHERE id_profesor = %s
        """, (id_profesor,))
        
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def obtenerInstrumentosPublicos():
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT i.id, i.titulo, i.descripcion, i.imagen, i.video_url, i.pdf_url, 
                   i.estado, p.nombre, p.apellido 
            FROM instrumentos i
            JOIN usuario p ON i.id_profesor = p.id
            WHERE i.estado = 'publico'
        """)
        
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def actualizar_instrumento(instrumento_id, titulo=None, descripcion=None, imagen=None, video_url=None, pdf_url=None, estado=None, id_profesor=None):
    """Actualiza un instrumento"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            updates = []
            params = []
            
            if titulo:
                updates.append("titulo = %s")
                params.append(titulo)
            if descripcion:
                updates.append("descripcion = %s")
                params.append(descripcion)
            if imagen:
                updates.append("imagen = %s")
                params.append(imagen)
            if video_url:
                updates.append("video_url = %s")
                params.append(video_url)
            if pdf_url:
                updates.append("pdf_url = %s")
                params.append(pdf_url)
            if estado:
                updates.append("estado = %s")
                params.append(estado)
            
            if not updates:
                return False
                
            query = f"UPDATE instrumentos SET {', '.join(updates)} WHERE id = %s"
            params.append(instrumento_id)
            
            if id_profesor:
                query += " AND id_profesor = %s"
                params.append(id_profesor)
            
            cursor.execute(query, tuple(params))
            connection.commit()
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al actualizar instrumento: {e}")
        return False
    finally:
        if connection:
            connection.close()

def eliminar_instrumento(instrumento_id, id_profesor=None):
    """Elimina un instrumento"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            if id_profesor:
                cursor.execute('''
                    DELETE FROM instrumentos
                    WHERE id = %s AND id_profesor = %s
                ''', (instrumento_id, id_profesor))
            else:
                cursor.execute('''
                    DELETE FROM instrumentos
                    WHERE id = %s
                ''', (instrumento_id,))
            connection.commit()
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al eliminar instrumento: {e}")
        return False
    finally:
        if connection:
            connection.close()

def obtener_instrumento_por_id(id_instrumento, id_profesor=None):
    connection = get_connection()
    cursor = connection.cursor()
    consulta = "SELECT * FROM instrumentos WHERE id = %s"
    params = [id_instrumento]
    if id_profesor:
        consulta += " AND id_profesor = %s"
        params.append(id_profesor)
    cursor.execute(consulta, params)
    fila = cursor.fetchone()
    cursor.close()
    connection.close()
    if fila:
        columnas = [desc[0] for desc in cursor.description]
        return dict(zip(columnas, fila))
    else:
        return None




def obtenerInstrumentosPublicosExcluyendoProfesor(id_profesor):
    connection = get_connection()

    cursor = connection.cursor(pymysql.cursors.DictCursor)  
    try:
        cursor.execute("""
            SELECT i.*, CONCAT(u.nombre, ' ', u.apellido) AS autor
            FROM instrumentos i
            JOIN usuario u ON i.id_profesor = u.id
            WHERE i.estado = 'publico' AND i.id_profesor != %s
        """, (id_profesor,))
        instrumentos = cursor.fetchall()
        return instrumentos
    except Exception as e:
        print(f"Error al obtener instrumentos públicos: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


# --------------------------------------------------
# Funciones para mi agenda
# --------------------------------------------------

def obtenereventos(profesor_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT id, titulo, tipo, fecha, hora_inicio, hora_fin, lugar, descripcion
            FROM eventos
            WHERE usuario_id = %s  -- Usamos usuario_id como la FK en la tabla eventos
            ORDER BY fecha, hora_inicio
        """, (profesor_id,))  # Recibe profesor_id como parámetro

        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener eventos: {e}")
        return []  # Devuelve una lista vacía en caso de error
    finally:
        cursor.close()
        connection.close()


def insertar_evento(profesor_id, titulo, tipo, fecha, hora_inicio, hora_fin, lugar, descripcion, estado="activo"):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO eventos (
                usuario_id, titulo, tipo, fecha, hora_inicio, hora_fin,
                lugar, descripcion, estado, creado_en
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            profesor_id,  # Aqui usamos profesor_id, que es el FK a usuario_id
            titulo, tipo, fecha, hora_inicio, hora_fin,
            lugar, descripcion, estado
        ))
        connection.commit()
        return cursor.lastrowid  # Devuelve el ID del evento insertado
    finally:
        cursor.close()
        connection.close()


def eliminar_evento(evento_id, usuario_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM eventos WHERE id = %s AND usuario_id = %s", (evento_id, usuario_id))
        connection.commit()
        return cursor.rowcount  # Devuelve cuántas filas se eliminaron
    finally:
        cursor.close()
        connection.close()



def actualizar_evento(evento_id, usuario_id, titulo, tipo, fecha, hora_inicio, hora_fin, lugar, descripcion, estado):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE eventos SET
                titulo = %s,
                tipo = %s,
                fecha = %s,
                hora_inicio = %s,
                hora_fin = %s,
                lugar = %s,
                descripcion = %s,
                estado = %s
            WHERE id = %s AND usuario_id = %s
        """, (
            titulo, tipo, fecha, hora_inicio, hora_fin,
            lugar, descripcion, estado, evento_id, usuario_id
        ))
        connection.commit()
        return cursor.rowcount  # Devuelve cuántas filas se actualizaron
    finally:
        cursor.close()
        connection.close()



def obtener_escuelas_profesor(id_profesor):
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT * FROM mis_escuelas 
                WHERE id_usuario = %s
                ORDER BY fecha_inicio DESC
            """
            cursor.execute(sql, (id_profesor,))
            return cursor.fetchall()
    finally:
        connection.close()

def obtener_reportes_profesor(id_profesor):
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT r.* FROM reportes r
                JOIN mis_escuelas e ON r.id_escuela = e.id_escuela
                WHERE e.id_usuario = %s
                ORDER BY r.fecha_reporte DESC
            """
            cursor.execute(sql, (id_profesor,))
            return cursor.fetchall()
    finally:
        connection.close()

def insertar_escuelas(nombre_escuela, direccion, telefono, id_usuario, fecha_creacion, fecha_inicio, fecha_cese):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO mis_escuelas (
                `nombre_escuela`, `direccion`, `telefono`, `id_usuario`, `fecha_creacion`, `fecha_inicio`, `fecha_cese`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre_escuela, direccion, telefono, id_usuario, fecha_creacion, fecha_inicio, fecha_cese
        ))
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()


def actualizar_escuela(id_escuela, nombre_escuela, direccion, telefono, fecha_inicio, 
                      fecha_cese, usuario_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
        UPDATE mis_escuelas 
        SET nombre_escuela = %s, 
            direccion = %s, 
            telefono = %s, 
            fecha_inicio = %s, 
            fecha_cese = %s
        WHERE id_escuela = %s AND id_usuario = %s
        """, (
            nombre_escuela, direccion, telefono, fecha_inicio, 
                             fecha_cese, id_escuela, usuario_id
        ))
        connection.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        connection.close()

def actualizar_reporte(id_reporte, id_escuela, tipo, descripcion, fecha_reporte,
                      nombre_alumno, apellido_alumno, usuario_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = """
        UPDATE reportes 
        SET id_escuela = %s,
            tipo = %s,
            descripcion = %s,
            fecha_reporte = %s,
            nombre_alumno = %s,
            apellido_alumno = %s
        WHERE id_reporte = %s AND id_usuario = %s
        """
        cursor.execute(query, (id_escuela, tipo, descripcion, fecha_reporte,
                             nombre_alumno, apellido_alumno, id_reporte, usuario_id))
        connection.commit()
        return cursor.rowcount
    except Exception as e:
        connection.rollback()
        raise e

def obtener_escuela_por_id(id_escuela, usuario_id):
    """Obtiene una escuela específica por ID verificando el usuario"""
    connection = get_connection()
    if connection is None:
        raise Exception("No se pudo establecer conexión con la base de datos")
    
    try:
        with connection.cursor() as cursor:  # Sin dictionary=True
            cursor.execute("""
                SELECT * FROM mis_escuelas 
                WHERE id_escuela = %s AND id_usuario = %s
            """, (id_escuela, usuario_id))
            return cursor.fetchone()  # Devuelve un diccionario por el DictCursor configurado
    finally:
        connection.close()

def eliminar_reportes_de_escuela(id_escuela):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            DELETE FROM reportes 
            WHERE id_escuela = %s
        """, (id_escuela,))
        connection.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        connection.close()


def obtener_reporte_por_id(report_id, user_id):
    """Get a specific report that belongs to the user"""
    connection = get_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT r.* FROM reportes r
                JOIN mis_escuelas e ON r.id_escuela = e.id_escuela
                WHERE r.id_reporte = %s AND e.id_usuario = %s
            """
            cursor.execute(query, (report_id, user_id))
            return cursor.fetchone()
    finally:
        connection.close()

def eliminar_reporte(report_id, user_id):
    """Delete a report verifying user ownership"""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # First verify the report belongs to the user
            cursor.execute("""
                SELECT r.id_reporte FROM reportes r
                JOIN mis_escuelas e ON r.id_escuela = e.id_escuela
                WHERE r.id_reporte = %s AND e.id_usuario = %s
            """, (report_id, user_id))
            
            if not cursor.fetchone():
                return 0  # Report doesn't exist or doesn't belong to user
                
            # If exists, proceed to delete
            cursor.execute("""
                DELETE FROM reportes 
                WHERE id_reporte = %s
            """, (report_id,))
            connection.commit()
            return cursor.rowcount
    except Exception as e:
        raise e
    finally:
        connection.close()

        
def eliminar_escuela(id_escuela, usuario_id):
    """Elimina una escuela verificando permisos"""
    connection = get_connection()
    if connection is None:
        raise Exception("No se pudo establecer conexión con la base de datos")
    
    try:
        with connection.cursor() as cursor:  # Elimina dictionary=True aquí
            # Primero verificar que la escuela pertenece al usuario
            cursor.execute("""
                SELECT id_escuela FROM mis_escuelas 
                WHERE id_escuela = %s AND id_usuario = %s
            """, (id_escuela, usuario_id))
            
            if not cursor.fetchone():
                return 0  # No se encontró la escuela o no pertenece al usuario
                
            # Si existe, proceder a eliminar
            cursor.execute("""
                DELETE FROM mis_escuelas 
                WHERE id_escuela = %s AND id_usuario = %s
            """, (id_escuela, usuario_id))
            # No necesitas connection.commit() porque tienes autocommit=True
            return cursor.rowcount
    except Exception as e:
        # Aunque tengas autocommit=True, es buena práctica manejar errores
        raise e
    finally:
        connection.close()



def insertar_reporte(tipo, descripcion, fecha_reporte, estado, id_escuela, id_usuario, nombre_alumno, apellido_alumno):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO reportes (
                tipo, descripcion, fecha_reporte, estado, id_escuela, id_usuario,
                nombre_alumno, apellido_alumno
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            tipo, descripcion, fecha_reporte, estado, id_escuela, id_usuario,
            nombre_alumno, apellido_alumno
        ))
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()

def eliminar_reportes_de_escuela(id_escuela):
    """Elimina todos los reportes asociados a una escuela"""
    connection = get_connection()
    if connection is None:
        raise Exception("No se pudo establecer conexión con la base de datos")
    
    try:
        with connection.cursor() as cursor:  # Sin dictionary=True
            cursor.execute("""
                DELETE FROM reportes 
                WHERE id_escuela = %s
            """, (id_escuela,))
            # No necesitas connection.commit() por el autocommit
            return cursor.rowcount
    except Exception as e:
        raise e
    finally:
        connection.close()
# --------------------------------------------------
# Funciones para educacion
# --------------------------------------------------

def obtener_recursos():
    connection = get_connection()
    cursor = connection.cursor() 
    cursor.execute("SELECT id, nombre, url, categoria, tamanio, fecha_subida FROM recursos")
    recursos = cursor.fetchall()  
    #print(recursos)
    connection.close()
    return recursos

# --------------------------------------------------
# Funciones para administrador
# --------------------------------------------------

def seleccionarUsuarios_Admin():
    """Obtiene todos los usuarios del sistema."""
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
             sql = "SELECT id, nombre, apellido, mail, rol FROM usuario WHERE rol = %s"
             cursor.execute(sql, ('profesor',)) 
             return cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error al consultar los datos de los usuarios: {e}")
        return []
    finally:
        connection.close()

def seleccionarUsuarios_Administrador():
    """Obtiene los usuarios con rol 'administrador' del sistema."""
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT id, nombre,apellido, mail, rol FROM usuario WHERE rol = %s"
            cursor.execute(sql, ('administrador',))  
            return cursor.fetchall()
            
    except pymysql.MySQLError as e:
        print(f"Error al consultar usuarios administradores: {e}")
        return []  
    finally:
        if 'connection' in locals() and connection.open:
            connection.close() 

def cambiar_rol(nuevo_rol, id_usuario):
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                UPDATE usuario SET
                    rol = %s
                WHERE id = %s
            """
            cursor.execute(sql, (nuevo_rol, id_usuario))
        connection.commit()
    except Exception as e:
        print(f"Error al cambiar el rol: {e}")
    finally:
        connection.close()

def editar_usuario_admin(id, nombre, apellido, email, rol):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = """
                UPDATE usuario
                SET nombre = %s, apellido = %s, mail = %s, rol = %s
                WHERE id = %s
            """
            cursor.execute(sql, (nombre, apellido, email, rol, id))
        connection.commit()
    except Exception as e:
        print(f"Error al editar admin: {e}")
    finally:
        connection.close()

def obtener_usuario_por_id(id):
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM usuario WHERE id = %s AND rol = 'administrador'"
            cursor.execute(sql, (id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener admin: {e}")
    finally:
        connection.close()

def eliminar_usuario_admin(id):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM usuario WHERE id = %s AND rol = 'administrador'"
            cursor.execute(sql, (id,))
        connection.commit()
    except Exception as e:
        print(f"Error al eliminar admin: {e}")
    finally:
        connection.close()



def crear_usuario_admin(nombre, apellido, email, password):
    try:
        password_hash = generate_password_hash(password)
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO usuario (nombre, apellido, mail, password, rol)
                VALUES (%s, %s, %s, %s, 'administrador')
            """
            cursor.execute(sql, (nombre, apellido, email, password_hash))
        connection.commit()
    except Exception as e:
        print(f"Error al crear admin: {e}")
    finally:
        connection.close()

def editar_profesor(id, nombre, apellido, email, rol):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = """
                UPDATE usuario
                SET nombre = %s, apellido = %s, mail = %s, rol = %s
                WHERE id = %s
            """
            cursor.execute(sql, (nombre, apellido, email, rol, id))
        connection.commit()
    except Exception as e:
        print(f"Error al editar profesor: {e}")
    finally:
        connection.close()


def obtener_profesor_por_id(id):
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM usuario WHERE id = %s AND rol = 'profesor'"
            cursor.execute(sql, (id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener profesor: {e}")
    finally:
        connection.close()

def eliminar_profesor(id):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM usuario WHERE id = %s AND rol = 'profesor'"
            cursor.execute(sql, (id,))
        connection.commit()
    except Exception as e:
        print(f"Error al eliminar profesor: {e}")
    finally:
        connection.close()


def crear_profesor(nombre, email, password):
    try:
        password_hash = generate_password_hash(password)
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO usuario (nombre, mail, password, rol)
                VALUES (%s, %s, %s, 'profesor')
            """
            cursor.execute(sql, (nombre, email, password_hash))
        connection.commit()
    except Exception as e:
        print(f"Error al crear profesor: {e}")
    finally:
        connection.close()




def contar_profesores():
    """Obtiene el número total de profesores registrados"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS total_profesores 
                FROM usuario
                WHERE rol = 'profesor'
            """)
            resultado = cursor.fetchone()
            return resultado['total_profesores'] if resultado else 0
    except pymysql.MySQLError as e:
        print(f"Error al contar profesores: {e}")
        return 0
    finally:
        if connection:
            connection.close()

def contar_proyectos():
    """Obtiene el número total de proyectos registrados"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS total_proyectos 
                FROM proyecto
                WHERE estado = 'terminado'
            """)
            resultado = cursor.fetchone()
            return resultado['total_proyectos'] if resultado else 0
    except pymysql.MySQLError as e:
        print(f"Error al contar proyectos: {e}")
        return 0
    finally:
        if connection:
            connection.close()

def contar_blog_posts():
    """Obtiene el número total de posts de blog"""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS total_blog_posts 
                FROM blog 
            """)
            resultado = cursor.fetchone()
            return resultado['total_blog_posts'] if resultado else 0
    except pymysql.MySQLError as e:
        print(f"Error al contar posts de blog: {e}")
        return 0
    finally:
        if connection:
            connection.close()


def seleccionarblog_Admin():
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM blog')
            resultado = cursor.fetchall()
            return resultado
    except pymysql.MySQLError as e:
        print(f"Error al consultar los datos de los blogs: {e}")
        return []
    finally:
        connection.close()

def seleccionarmusica_Admin():
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM canciones')
            resultado = cursor.fetchall()
            return resultado
    except pymysql.MySQLError as e:
        print(f"Error al consultar los datos de las canciones: {e}")
        return []
    finally:
        connection.close()


def seleccionarvideo_Admin():
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM video')
            resultado = cursor.fetchall()
            return resultado
    except pymysql.MySQLError as e:
        print(f"Error al consultar los datos de los videos: {e}")
        return []
    finally:
        connection.close()

def seleccionarproyecto_Admin():
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM proyecto')
            resultado = cursor.fetchall()
            return resultado
    except pymysql.MySQLError as e:
        print(f"Error al consultar los datos de los proyectos: {e}")
        return []
    finally:
        connection.close()

def seleccionarRecursos_Admin():
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM recursos')
            resultado = cursor.fetchall()
            return resultado
    except pymysql.MySQLError as e:
        print(f"Error al consultar los datos de los recursos: {e}")
        return []
    finally:
        connection.close()

def crear_blog(nombre, contenido, imagen, id_profesor=None, id_admin=None):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO blog (nombre, contenido, imagen, id_profesor, id_admin)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, contenido, imagen, id_profesor, id_admin))
        connection.commit()
    except Exception as e:
        print(f"Error al crear el blog: {e}")
    finally:
        connection.close()


def editar_blog(id_blog, nombre, contenido, imagen):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = """
                UPDATE blog SET
                    nombre = %s,
                    contenido = %s,
                    imagen = %s
                WHERE id = %s
            """
            cursor.execute(sql, (nombre, contenido, imagen, id_blog))
        connection.commit()
    except Exception as e:
        print(f"Error al editar el blog: {e}")
    finally:
        connection.close()

def eliminar_blog(id_blog):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM blog WHERE id = %s"
            cursor.execute(sql, (id_blog,))
        connection.commit()
    except Exception as e:
        print(f"Error al eliminar el blog: {e}")
    finally:
        connection.close()


def crear_musica(titulo, artista, album, ruta_archivo, categoria):
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO canciones (titulo, artista, album, ruta_archivo, categoria)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (titulo, artista, album, ruta_archivo, categoria))
        connection.commit()
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error al crear música en la base de datos: {e}")
        raise  
    finally:
        if connection:
            connection.close()




def editar_musica(id, titulo, artista, album, categoria, ruta_archivo=None):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            if ruta_archivo:
                sql = """
                    UPDATE canciones
                    SET titulo = %s, artist = %s, album = %s, categoria = %s, ruta_archivo = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (titulo, artista, album, categoria, ruta_archivo, id))
            else:
                sql = """
                    UPDATE canciones
                    SET titulo = %s, artist = %s, album = %s, categoria = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (titulo, artista, album, categoria, id))
        connection.commit()
    finally:
        connection.close()



def eliminar_musica(id):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM canciones WHERE id = %s"
            cursor.execute(sql, (id,))
        connection.commit()
    finally:
        connection.close()


def obtener_musica_por_id(id):
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM canciones WHERE id = %s"
            cursor.execute(sql, (id,))
            return cursor.fetchone()
    finally:
        connection.close()


def seleccionarmusica_Admin():
    try:
        connection = get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM canciones ORDER BY id DESC"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

# --------------------------------------------------
# Inicialización de tablas (ejecutar al inicio)
# --------------------------------------------------
if __name__ == '__main__':
    crear_todas_tablas()