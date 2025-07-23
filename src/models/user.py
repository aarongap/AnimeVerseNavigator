# src/models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, email, password_hash=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

# src/models/anime.py
class Anime:
    def __init__(self, id, titulo, descripcion, anio_lanzamiento, estudio_productor, promedio_calificacion):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.anio_lanzamiento = anio_lanzamiento
        self.estudio_productor = estudio_productor
        self.promedio_calificacion = promedio_calificacion