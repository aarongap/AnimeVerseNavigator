-- Función: fn_obtener_animes_por_genero
CREATE OR REPLACE FUNCTION fn_obtener_animes_por_genero(p_nombre_genero VARCHAR)
RETURNS TABLE (
    id INTEGER,
    titulo VARCHAR,
    descripcion TEXT,
    anio_lanzamiento INTEGER,
    estudio_productor VARCHAR,
    promedio_calificacion NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        A.id,
        A.titulo,
        A.descripcion,
        A.anio_lanzamiento,
        A.estudio_productor,
        A.promedio_calificacion
    FROM Animes A
    JOIN Animes_Generos AG ON A.id = AG.anime_id
    JOIN Generos G ON AG.genero_id = G.id
    WHERE G.nombre_genero ILIKE p_nombre_genero; -- ILIKE para búsqueda insensible a mayúsculas/minúsculas
END;
$$ LANGUAGE plpgsql;

-- Función: fn_calcular_popularidad_anime
CREATE OR REPLACE FUNCTION fn_calcular_popularidad_anime(p_anime_id INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    v_total_listas INTEGER;
    v_avg_calificacion NUMERIC(3, 2);
BEGIN
    SELECT COUNT(*) INTO v_total_listas
    FROM Lista_Ver
    WHERE anime_id = p_anime_id;

    SELECT promedio_calificacion INTO v_avg_calificacion
    FROM Animes
    WHERE id = p_anime_id;

    -- Fórmula simple de popularidad: (cantidad de veces en listas * 0.5) + (calificación promedio * 5)
    -- Ajusta los pesos según lo que consideres más "popular"
    RETURN (v_total_listas * 0.5) + (COALESCE(v_avg_calificacion, 0) * 5);
END;
$$ LANGUAGE plpgsql;

-- Procedimiento Almacenado: sp_registrar_nuevo_anime (CORREGIDO Y MEJORADO)
CREATE OR REPLACE PROCEDURE sp_registrar_nuevo_anime(
    IN p_titulo VARCHAR,
    IN p_descripcion TEXT,
    IN p_anio_lanzamiento INTEGER,
    IN p_estudio_productor VARCHAR,
    IN p_generos_array VARCHAR[] -- Array de nombres de géneros
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_anime_id INTEGER;
    v_genero_id INTEGER;
    v_genero_nombre VARCHAR;
BEGIN
    -- El manejo de la transacción (COMMIT/ROLLBACK) se hace desde la aplicación Python.
    -- Este bloque BEGIN/EXCEPTION/END es para manejo de excepciones internas
    -- y para re-lanzar el error al Python si algo falla dentro.
    BEGIN
        -- Intentar insertar el anime. Si el título ya existe, no hacer nada (ON CONFLICT DO NOTHING).
        -- Esto evita errores si un anime se intenta añadir dos veces.
        INSERT INTO Animes (titulo, descripcion, anio_lanzamiento, estudio_productor)
        VALUES (p_titulo, p_descripcion, p_anio_lanzamiento, p_estudio_productor)
        ON CONFLICT (titulo) DO NOTHING -- Ignora si el título ya existe
        RETURNING id INTO v_anime_id;

        -- Si v_anime_id es NULL, significa que el anime ya existía.
        -- En ese caso, obtenemos su ID para poder asociar los géneros.
        IF v_anime_id IS NULL THEN
            SELECT id INTO v_anime_id FROM Animes WHERE titulo = p_titulo;
            -- Opcionalmente, puedes RAISE NOTICE 'El anime ya existe, se actualizarán los géneros.'
        END IF;

        -- Solo procesar géneros si tenemos un ID de anime válido
        IF v_anime_id IS NOT NULL THEN
            FOREACH v_genero_nombre IN ARRAY p_generos_array LOOP
                -- Intentar obtener el ID del género existente, o insertarlo si no existe
                SELECT id INTO v_genero_id FROM Generos WHERE nombre_genero ILIKE v_genero_nombre;
                IF v_genero_id IS NULL THEN
                    INSERT INTO Generos (nombre_genero)
                    VALUES (INITCAP(v_genero_nombre)) -- Capitalizar la primera letra
                    RETURNING id INTO v_genero_id;
                END IF;

                -- Insertar en la tabla pivote, manejando conflictos para evitar duplicados en Animes_Generos
                INSERT INTO Animes_Generos (anime_id, genero_id)
                VALUES (v_anime_id, v_genero_id)
                ON CONFLICT (anime_id, genero_id) DO NOTHING; -- Ignora si la relación ya existe
            END LOOP;
        ELSE
            -- Si no se pudo obtener ni insertar el anime (ej. algún error inesperado previo),
            -- lanzamos una excepción para que el Python lo maneje.
            RAISE EXCEPTION 'No se pudo crear o encontrar el anime para asignar géneros.';
        END IF;

    EXCEPTION
        WHEN OTHERS THEN
            -- No usar COMMIT o ROLLBACK aquí.
            -- Simplemente re-lanzamos la excepción para que la aplicación Python la capture.
            RAISE EXCEPTION 'Error interno al procesar el registro del anime: %', SQLERRM;
    END;
END;
$$;

-- Procedimiento Almacenado: sp_actualizar_progreso_visualizacion
CREATE OR REPLACE PROCEDURE sp_actualizar_progreso_visualizacion(
    IN p_usuario_id INTEGER,
    IN p_anime_id INTEGER,
    IN p_nuevo_episodio INTEGER DEFAULT NULL,
    IN p_nuevo_estado VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE Lista_Ver
    SET
        episodio_actual = COALESCE(p_nuevo_episodio, episodio_actual),
        estado_visualizacion = COALESCE(p_nuevo_estado, estado_visualizacion),
        fecha_fin = CASE WHEN p_nuevo_estado = 'Completado' THEN CURRENT_TIMESTAMP ELSE fecha_fin END
    WHERE usuario_id = p_usuario_id AND anime_id = p_anime_id;

    IF NOT FOUND THEN
        -- Si no existe en la lista, lo insertamos
        INSERT INTO Lista_Ver (usuario_id, anime_id, estado_visualizacion, episodio_actual, fecha_inicio, fecha_fin)
        VALUES (p_usuario_id, p_anime_id, COALESCE(p_nuevo_estado, 'Viendo'), COALESCE(p_nuevo_episodio, 1), CURRENT_TIMESTAMP, NULL);
    END IF;
END;
$$;


-- Procedimiento Almacenado: sp_obtener_recomendaciones_personalizadas (simulado con AI básica)
-- Este procedimiento es más conceptual para el proyecto. La lógica "AI" real se manejaría en Python.
CREATE OR REPLACE PROCEDURE sp_obtener_recomendaciones_personalizadas(
    IN p_usuario_id INTEGER,
    OUT recomendado_anime_id INTEGER,
    OUT recomendado_titulo VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- Cursor para simular iteración sobre animes no vistos o animes con géneros similares
    cur_animes CURSOR FOR
        SELECT A.id, A.titulo
        FROM Animes A
        WHERE A.id NOT IN (SELECT LV.anime_id FROM Lista_Ver LV WHERE LV.usuario_id = p_usuario_id)
        ORDER BY RANDOM() -- En una implementación real, esto sería una lógica de recomendación
        LIMIT 10; -- Limitar para no procesar demasiado

    v_anime_id INTEGER;
    v_titulo VARCHAR;
    v_generos_favoritos VARCHAR[];
    v_genero_similar_id INTEGER;
    v_found BOOLEAN := FALSE;
BEGIN
    -- Simulación simple de "AI": encontrar géneros favoritos del usuario
    SELECT ARRAY_AGG(DISTINCT G.nombre_genero)
    INTO v_generos_favoritos
    FROM Calificaciones_Reseñas CR
    JOIN Animes_Generos AG ON CR.anime_id = AG.anime_id
    JOIN Generos G ON AG.genero_id = G.id
    WHERE CR.usuario_id = p_usuario_id AND CR.calificacion >= 7; -- Animes que el usuario calificó bien

    -- Si el usuario tiene géneros favoritos, intentar recomendar de esos
    IF ARRAY_LENGTH(v_generos_favoritos, 1) > 0 THEN
        -- Elegir un género favorito al azar
        SELECT G.id INTO v_genero_similar_id
        FROM Generos G
        WHERE G.nombre_genero = v_generos_favoritos[FLOOR(RANDOM() * ARRAY_LENGTH(v_generos_favoritos, 1) + 1)];

        -- Buscar un anime no visto en ese género
        OPEN cur_animes;
        LOOP
            FETCH cur_animes INTO v_anime_id, v_titulo;
            EXIT WHEN NOT FOUND;

            IF EXISTS (SELECT 1 FROM Animes_Generos AG WHERE AG.anime_id = v_anime_id AND AG.genero_id = v_genero_similar_id) THEN
                recomendado_anime_id := v_anime_id;
                recomendado_titulo := v_titulo;
                v_found := TRUE;
                EXIT;
            END IF;
        END LOOP;
        CLOSE cur_animes;
    END IF;

    -- Si no se encontró nada por géneros o no hay géneros favoritos, dar una recomendación aleatoria
    IF NOT v_found THEN
        SELECT A.id, A.titulo
        INTO recomendado_anime_id, recomendado_titulo
        FROM Animes A
        WHERE A.id NOT IN (SELECT LV.anime_id FROM Lista_Ver LV WHERE LV.usuario_id = p_usuario_id)
        ORDER BY RANDOM()
        LIMIT 1;
    END IF;

    IF recomendado_anime_id IS NULL THEN
        RAISE NOTICE 'No hay animes disponibles para recomendar al usuario %.', p_usuario_id;
    END IF;
END;
$$;