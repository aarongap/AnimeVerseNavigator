from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.database import get_db_connection
from src.ai_service import AnimeRecommender # Importa tu servicio de IA
from src.models.anime import Anime

anime_bp = Blueprint('anime', __name__)
recommender = AnimeRecommender() # Instancia el recomendador

@anime_bp.route('/animes')
@login_required
def list_animes():
    conn = None
    animes = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, descripcion, anio_lanzamiento, estudio_productor, promedio_calificacion FROM Animes ORDER BY titulo;")
        animes_data = cur.fetchall()
        for row in animes_data:
            animes.append(Anime(*row))
        cur.close()
    except Exception as e:
        flash(f'Error al cargar animes: {e}')
    finally:
        if conn:
            conn.close()
    return render_template('animes_list.html', animes=animes) # Crea este template

@anime_bp.route('/anime/<int:anime_id>')
@login_required
def anime_detail(anime_id):
    conn = None
    anime = None
    reviews = []
    user_list_status = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Obtener detalles del anime
        cur.execute("SELECT id, titulo, descripcion, anio_lanzamiento, estudio_productor, promedio_calificacion FROM Animes WHERE id = %s;", (anime_id,))
        anime_data = cur.fetchone()
        if anime_data:
            anime = Anime(*anime_data)
        
        # Obtener reseñas
        cur.execute("""
            SELECT CR.resena, CR.calificacion, U.username, CR.fecha_creacion
            FROM Calificaciones_Reseñas CR
            JOIN Usuarios U ON CR.usuario_id = U.id
            WHERE CR.anime_id = %s
            ORDER BY CR.fecha_creacion DESC;
        """, (anime_id,))
        reviews = cur.fetchall()

        # Obtener estado en la lista del usuario actual
        cur.execute("""
            SELECT estado_visualizacion, episodio_actual, fecha_inicio, fecha_fin
            FROM Lista_Ver
            WHERE usuario_id = %s AND anime_id = %s;
        """, (current_user.id, anime_id))
        user_list_status = cur.fetchone()

        cur.close()
    except Exception as e:
        flash(f'Error al cargar detalles del anime: {e}')
    finally:
        if conn:
            conn.close()
    
    if not anime:
        flash('Anime no encontrado.')
        return redirect(url_for('anime.list_animes'))
    return render_template('anime_detail.html', anime=anime, reviews=reviews, user_list_status=user_list_status)


@anime_bp.route('/add_review/<int:anime_id>', methods=['POST'])
@login_required
def add_review(anime_id):
    calificacion = request.form.get('calificacion')
    resena = request.form.get('resena')

    if not calificacion or not resena:
        flash('La calificación y la reseña son obligatorias.')
        return redirect(url_for('anime.anime_detail', anime_id=anime_id))

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Calificaciones_Reseñas (usuario_id, anime_id, calificacion, resena)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (usuario_id, anime_id) DO UPDATE SET
                calificacion = EXCLUDED.calificacion,
                resena = EXCLUDED.resena,
                fecha_creacion = CURRENT_TIMESTAMP;
        """, (current_user.id, anime_id, int(calificacion), resena))
        conn.commit()
        flash('Reseña guardada exitosamente. El promedio de calificación ha sido actualizado.')
    except Exception as e:
        flash(f'Error al guardar reseña: {e}')
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
    return redirect(url_for('anime.anime_detail', anime_id=anime_id))


@anime_bp.route('/update_list_status/<int:anime_id>', methods=['POST'])
@login_required
def update_list_status(anime_id):
    estado = request.form.get('estado')
    episodio = request.form.get('episodio', type=int)

    if not estado:
        flash('El estado es obligatorio.')
        return redirect(url_for('anime.anime_detail', anime_id=anime_id))
    
    # Llamar al procedimiento almacenado
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CALL sp_actualizar_progreso_visualizacion(%s, %s, %s, %s);",
                    (current_user.id, anime_id, episodio, estado))
        conn.commit()
        flash('Estado de visualización actualizado.')
    except Exception as e:
        flash(f'Error al actualizar estado: {e}')
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
    return redirect(url_for('anime.anime_detail', anime_id=anime_id))


@anime_bp.route('/recommendations')
@login_required
def show_recommendations():
    recommendations = recommender.get_recommendations(current_user.id)
    # Puedes buscar los detalles completos de los animes recomendados si es necesario
    # Por ahora, solo pasamos los IDs y títulos del AI Service
    return render_template('recommendations.html', recommendations=recommendations) # Crea este template

# Para demostrar el procedimiento de SQL directamente
@anime_bp.route('/admin/add_new_anime', methods=['GET', 'POST'])
@login_required
def admin_add_anime():
    # Aquí podrías poner una verificación de rol para usuarios admin
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        anio = request.form.get('anio', type=int)
        estudio = request.form['estudio']
        generos_str = request.form['generos'] # CSV string like "Accion,Aventura"
        generos_array = [g.strip() for g in generos_str.split(',') if g.strip()]

        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("CALL sp_registrar_nuevo_anime(%s, %s, %s, %s, %s);",
                        (titulo, descripcion, anio, estudio, generos_array))
            conn.commit()
            flash('Anime registrado exitosamente.')
            return redirect(url_for('anime.list_animes'))
        except Exception as e:
            flash(f'Error al registrar anime: {e}')
            if conn:
                conn.rollback()
        finally:
            if conn:
                cur.close()
                conn.close()
    return render_template('admin_add_anime.html') # Crea este template