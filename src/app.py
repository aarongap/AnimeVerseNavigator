from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from src.controllers.auth_controller import auth_bp, load_user
from src.controllers.anime_controller import anime_bp
import os
from dotenv import load_dotenv
from src.database import get_db_connection

load_dotenv() # Carga las variables de entorno

app = Flask(__name__,
            template_folder='templates',
            static_folder='../static') # Ajusta static_folder
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key_if_not_set')

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # Vista a la que redirigir si no está logueado

@login_manager.user_loader
def user_loader(user_id):
    return load_user(user_id)

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(anime_bp)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = None
    user_animes = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Consulta avanzada: Animes en la lista del usuario con su estado
        cur.execute("""
            SELECT A.id, A.titulo, LV.estado_visualizacion, LV.episodio_actual
            FROM Lista_Ver LV
            JOIN Animes A ON LV.anime_id = A.id
            WHERE LV.usuario_id = %s
            ORDER BY A.titulo;
        """, (current_user.id,))
        user_animes = cur.fetchall()
        cur.close()
    except Exception as e:
        flash(f'Error al cargar tu lista de animes: {e}')
    finally:
        if conn:
            conn.close()

    return render_template('dashboard.html', user_animes=user_animes)

@app.errorhandler(401)
def unauthorized(error):
    flash("Necesitas iniciar sesión para acceder a esta página.")
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    from src.database import execute_sql_file
    # Asegúrate de que los scripts de BD se ejecuten solo UNA VEZ,
    # o cuando se necesite refrescar la DB.
    # Descomenta solo si vas a re-crear la base de datos localmente
    # execute_sql_file('database/create_tables.sql')
    # execute_sql_file('database/functions_procedures.sql')
    # execute_sql_file('database/triggers.sql')
    # execute_sql_file('database/sample_data.sql')

    app.run(debug=True) # debug=True para desarrollo, cambiar a False en producción