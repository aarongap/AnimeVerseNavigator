-- Tabla: Usuarios
CREATE TABLE Usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Animes
CREATE TABLE Animes (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) UNIQUE NOT NULL,
    descripcion TEXT,
    anio_lanzamiento INTEGER,
    estudio_productor VARCHAR(100),
    promedio_calificacion NUMERIC(3, 2) DEFAULT 0.00, -- Actualizado por trigger
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Generos
CREATE TABLE Generos (
    id SERIAL PRIMARY KEY,
    nombre_genero VARCHAR(50) UNIQUE NOT NULL
);

-- Tabla pivote: Animes_Generos (relación muchos a muchos)
CREATE TABLE Animes_Generos (
    anime_id INTEGER NOT NULL REFERENCES Animes(id) ON DELETE CASCADE,
    genero_id INTEGER NOT NULL REFERENCES Generos(id) ON DELETE CASCADE,
    PRIMARY KEY (anime_id, genero_id)
);

-- Tabla: Calificaciones_Reseñas
CREATE TABLE Calificaciones_Reseñas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    anime_id INTEGER NOT NULL REFERENCES Animes(id) ON DELETE CASCADE,
    calificacion INTEGER CHECK (calificacion >= 1 AND calificacion <= 10),
    resena TEXT,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (usuario_id, anime_id) -- Un usuario solo puede calificar un anime una vez
);

-- Tabla: Lista_Ver (seguimiento de visualización)
CREATE TABLE Lista_Ver (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    anime_id INTEGER NOT NULL REFERENCES Animes(id) ON DELETE CASCADE,
    estado_visualizacion VARCHAR(20) DEFAULT 'Pendiente' CHECK (estado_visualizacion IN ('Pendiente', 'Viendo', 'Completado', 'Abandonado')),
    episodio_actual INTEGER DEFAULT 0,
    fecha_inicio TIMESTAMP WITH TIME ZONE,
    fecha_fin TIMESTAMP WITH TIME ZONE,
    UNIQUE (usuario_id, anime_id) -- Un anime solo puede estar una vez en la lista de un usuario
);

-- Tabla de Auditoría (para el trigger de eliminación)
CREATE TABLE Auditoria_Animes (
    id SERIAL PRIMARY KEY,
    anime_id INTEGER,
    titulo_anime VARCHAR(255),
    accion VARCHAR(50) NOT NULL,
    fecha_accion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario_accion VARCHAR(100) DEFAULT CURRENT_USER
);