-- Datos de prueba para Generos
INSERT INTO Generos (nombre_genero) VALUES
('Acción'), ('Aventura'), ('Comedia'), ('Drama'), ('Fantasia'),
('Ciencia Ficción'), ('Romance'), ('Slice of Life'), ('Mecha'), ('Misterio');

-- Datos de prueba para Usuarios (contraseñas en texto plano, en producción usar bcrypt)
INSERT INTO Usuarios (username, email, password_hash) VALUES
('juanito', 'juanito@example.com', 'password123'),
('mariaperez', 'maria@example.com', 'securepass'),
('animesfan', 'fan@example.com', 'animelover');

-- Datos de prueba para Animes
INSERT INTO Animes (titulo, descripcion, anio_lanzamiento, estudio_productor) VALUES
('Attack on Titan', 'La humanidad lucha por sobrevivir contra titanes gigantes.', 2013, 'Wit Studio'),
('One Piece', 'Monkey D. Luffy busca el One Piece para convertirse en el Rey de los Piratas.', 1999, 'Toei Animation'),
('Spy x Family', 'Una familia disfuncional con un espía, una asesina y una telépata.', 2022, 'Wit Studio / CloverWorks'),
('Mushoku Tensei: Jobless Reincarnation', 'Un hombre reencarna en un mundo de fantasía.', 2021, 'Studio Bind'),
('Frieren: Beyond Journey''s End', 'Una elfa maga reflexiona sobre el tiempo y la amistad.', 2023, 'Madhouse');

-- Datos de prueba para Animes_Generos
-- Attack on Titan
INSERT INTO Animes_Generos (anime_id, genero_id) VALUES
((SELECT id FROM Animes WHERE titulo = 'Attack on Titan'), (SELECT id FROM Generos WHERE nombre_genero = 'Acción')),
((SELECT id FROM Animes WHERE titulo = 'Attack on Titan'), (SELECT id FROM Generos WHERE nombre_genero = 'Drama')),
((SELECT id FROM Animes WHERE titulo = 'Attack on Titan'), (SELECT id FROM Generos WHERE nombre_genero = 'Fantasia'));
-- One Piece
INSERT INTO Animes_Generos (anime_id, genero_id) VALUES
((SELECT id FROM Animes WHERE titulo = 'One Piece'), (SELECT id FROM Generos WHERE nombre_genero = 'Aventura')),
((SELECT id FROM Animes WHERE titulo = 'One Piece'), (SELECT id FROM Generos WHERE nombre_genero = 'Acción')),
((SELECT id FROM Animes WHERE titulo = 'One Piece'), (SELECT id FROM Generos WHERE nombre_genero = 'Comedia'));
-- Spy x Family
INSERT INTO Animes_Generos (anime_id, genero_id) VALUES
((SELECT id FROM Animes WHERE titulo = 'Spy x Family'), (SELECT id FROM Generos WHERE nombre_genero = 'Comedia')),
((SELECT id FROM Animes WHERE titulo = 'Spy x Family'), (SELECT id FROM Generos WHERE nombre_genero = 'Acción')),
((SELECT id FROM Animes WHERE titulo = 'Spy x Family'), (SELECT id FROM Generos WHERE nombre_genero = 'Slice of Life'));
-- Mushoku Tensei
INSERT INTO Animes_Generos (anime_id, genero_id) VALUES
((SELECT id FROM Animes WHERE titulo = 'Mushoku Tensei: Jobless Reincarnation'), (SELECT id FROM Generos WHERE nombre_genero = 'Fantasia')),
((SELECT id FROM Animes WHERE titulo = 'Mushoku Tensei: Jobless Reincarnation'), (SELECT id FROM Generos WHERE nombre_genero = 'Aventura'));
-- Frieren
INSERT INTO Animes_Generos (anime_id, genero_id) VALUES
((SELECT id FROM Animes WHERE titulo = 'Frieren: Beyond Journey''s End'), (SELECT id FROM Generos WHERE nombre_genero = 'Fantasia')),
((SELECT id FROM Animes WHERE titulo = 'Frieren: Beyond Journey''s End'), (SELECT id FROM Generos WHERE nombre_genero = 'Aventura')),
((SELECT id FROM Animes WHERE titulo = 'Frieren: Beyond Journey''s End'), (SELECT id FROM Generos WHERE nombre_genero = 'Drama'));

-- Datos de prueba para Calificaciones_Reseñas
INSERT INTO Calificaciones_Reseñas (usuario_id, anime_id, calificacion, resena) VALUES
((SELECT id FROM Usuarios WHERE username = 'juanito'), (SELECT id FROM Animes WHERE titulo = 'Attack on Titan'), 9, 'Una obra maestra, la trama es increíble.'),
((SELECT id FROM Usuarios WHERE username = 'juanito'), (SELECT id FROM Animes WHERE titulo = 'One Piece'), 8, 'Largo, pero vale la pena cada episodio.'),
((SELECT id FROM Usuarios WHERE username = 'mariaperez'), (SELECT id FROM Animes WHERE titulo = 'Spy x Family'), 10, 'Demasiado tierna y divertida!'),
((SELECT id FROM Usuarios WHERE username = 'mariaperez'), (SELECT id FROM Animes WHERE titulo = 'Frieren: Beyond Journey''s End'), 9, 'Un anime muy reflexivo y hermoso.'),
((SELECT id FROM Usuarios WHERE username = 'animesfan'), (SELECT id FROM Animes WHERE titulo = 'Attack on Titan'), 8, 'Buena acción.'),
((SELECT id FROM Usuarios WHERE username = 'animesfan'), (SELECT id FROM Animes WHERE titulo = 'Mushoku Tensei: Jobless Reincarnation'), 7, 'Interesante concepto isekai.');

-- Datos de prueba para Lista_Ver
INSERT INTO Lista_Ver (usuario_id, anime_id, estado_visualizacion, episodio_actual, fecha_inicio) VALUES
((SELECT id FROM Usuarios WHERE username = 'juanito'), (SELECT id FROM Animes WHERE titulo = 'Attack on Titan'), 'Completado', 87, '2020-01-15'),
((SELECT id FROM Usuarios WHERE username = 'juanito'), (SELECT id FROM Animes WHERE titulo = 'One Piece'), 'Viendo', 1000, '2021-03-01'),
((SELECT id FROM Usuarios WHERE username = 'mariaperez'), (SELECT id FROM Animes WHERE titulo = 'Spy x Family'), 'Completado', 25, '2023-05-10'),
((SELECT id FROM Usuarios WHERE username = 'mariaperez'), (SELECT id FROM Animes WHERE titulo = 'Mushoku Tensei: Jobless Reincarnation'), 'Pendiente', 0, NULL),
((SELECT id FROM Usuarios WHERE username = 'animesfan'), (SELECT id FROM Animes WHERE titulo = 'Frieren: Beyond Journey''s End'), 'Viendo', 15, '2023-11-01');