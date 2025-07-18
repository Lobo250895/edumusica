import bcrypt
import re
from datetime import datetime
from werkzeug.security import generate_password_hash

class Usuario:
    def __init__(self, id=None, nombre=None, apellido=None, imagen_perfil=None, dni=None, 
                 direccion=None, telefono=None, mail=None, contraseña=None, rol=None, firebase_id=None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.imagen_perfil = imagen_perfil
        self.dni = dni
        self.direccion = direccion
        self.telefono = telefono
        self.mail = mail
        self.contraseña = contraseña
        self.rol = rol
        self.firebase_id = firebase_id

    @staticmethod
    def validar_email(email):
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

    @staticmethod
    def validar_telefono(telefono):
        return telefono.isdigit() and len(telefono) in range(10, 16)

    def encriptar_contraseña(self):
        if self.contraseña:
            self.contraseña = bcrypt.hashpw(self.contraseña.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

class Admin(Usuario):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rol = 'admin'


class Proyecto:
    def __init__(self, id=None, nombre=None, autor=None, fecha_subida=None, proyecto=None, 
                 estado=None, es_publico=False, autor_id=None):
        self.id = id
        self.nombre = nombre
        self.autor = autor
        self.fecha_subida = fecha_subida
        self.proyecto = proyecto
        self.estado = estado
        self.es_publico = es_publico
        self.autor_id = autor_id

class Cancion:
    def __init__(self, id=None, titulo=None, artista=None, album=None, ruta_archivo=None, categoria=None):
        self.id = id
        self.titulo = titulo
        self.artista = artista
        self.album = album
        self.ruta_archivo = ruta_archivo
        self.categoria = categoria

class Blog:
    def __init__(self, id=None, nombre=None, contenido=None, id_profesor=None, id_admin=None, 
                 fecha_creacion=None, imagen=None, vistas=0):
        self.id = id
        self.nombre = nombre
        self.contenido = contenido
        self.id_profesor = id_profesor
        self.id_admin = id_admin
        self.fecha_creacion = fecha_creacion
        self.imagen = imagen
        self.vistas = vistas

class Comentario:
    def __init__(self, id=None, id_blog=None, id_usuario=None, comentario=None, fecha=None, parent_id=None):
        self.id = id
        self.id_blog = id_blog
        self.id_usuario = id_usuario
        self.comentario = comentario
        self.fecha = fecha
        self.parent_id = parent_id

class Instrumento:
    def __init__(self, id=None, titulo=None, descripcion=None, imagen=None, video_url=None, 
                 pdf_url=None, id_profesor=None, estado='privado'):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.imagen = imagen
        self.video_url = video_url
        self.pdf_url = pdf_url
        self.id_profesor = id_profesor
        self.estado = estado

class Evento:
    def __init__(self, id=None, titulo=None, descripcion=None, fecha_inicio=None, fecha_fin=None, 
                 ubicacion=None, id_profesor=None, color=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.ubicacion = ubicacion
        self.id_profesor = id_profesor
        self.color = color

class Escuela:
    def __init__(self, id=None, nombre=None, direccion=None, telefono=None, id_profesor=None):
        self.id = id
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.id_profesor = id_profesor

class Recurso:
    def __init__(self, id=None, nombre=None, url=None, categoria=None, tamanio=None, fecha_subida=None):
        self.id = id
        self.nombre = nombre
        self.url = url
        self.categoria = categoria
        self.tamanio = tamanio
        self.fecha_subida = fecha_subida

class Video:
    def __init__(self, id=None, nombre=None, ruta_archivo=None, genero=None, imagen=None, 
                 id_profesor=None, fecha_subida=None):
        self.id = id
        self.nombre = nombre
        self.ruta_archivo = ruta_archivo
        self.genero = genero
        self.imagen = imagen
        self.id_profesor = id_profesor
        self.fecha_subida = fecha_subida

class Notificacion:
    def __init__(self, id=None, usuario_id=None, mensaje=None, tipo=None, visto=False, fecha=None):
        self.id = id
        self.usuario_id = usuario_id
        self.mensaje = mensaje
        self.tipo = tipo
        self.visto = visto
        self.fecha = fecha