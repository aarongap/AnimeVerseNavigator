-- Trigger 1: Actualizar el promedio de calificación de un anime
-- Función que el trigger ejecutará
CREATE OR REPLACE FUNCTION func_actualizar_promedio_calificacion()
RETURNS TRIGGER AS $$
BEGIN
    -- Recalcular el promedio para el anime afectado
    UPDATE Animes
    SET promedio_calificacion = (
        SELECT AVG(calificacion)
        FROM Calificaciones_Reseñas
        WHERE anime_id = NEW.anime_id
    )
    WHERE id = NEW.anime_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Definición del trigger
CREATE TRIGGER trg_actualizar_promedio_calificacion
AFTER INSERT OR UPDATE ON Calificaciones_Reseñas
FOR EACH ROW
EXECUTE FUNCTION func_actualizar_promedio_calificacion();

-- Trigger 2: Auditoría de eliminación de animes
-- Función que el trigger ejecutará
CREATE OR REPLACE FUNCTION func_auditoria_eliminacion_anime()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Auditoria_Animes (anime_id, titulo_anime, accion, usuario_accion)
    VALUES (OLD.id, OLD.titulo, 'ELIMINADO', CURRENT_USER); -- CURRENT_USER obtiene el usuario de la DB
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Definición del trigger
CREATE TRIGGER trg_auditoria_eliminacion_anime
AFTER DELETE ON Animes
FOR EACH ROW
EXECUTE FUNCTION func_auditoria_eliminacion_anime();