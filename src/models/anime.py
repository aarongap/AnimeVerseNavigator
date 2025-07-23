# src/models/anime.py
class Anime:
    def __init__(self, id, titulo, descripcion, anio_lanzamiento, estudio_productor, promedio_calificacion):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.anio_lanzamiento = anio_lanzamiento
        self.estudio_productor = estudio_productor
        self.promedio_calificacion = promedio_calificacion