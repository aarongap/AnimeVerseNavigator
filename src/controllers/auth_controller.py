from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.database import get_db_connection
from src.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            flash('Todos los campos son obligatorios.')
            return render_template('index.html', show_register=True)

        password_hash = generate_password_hash(password)
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO Usuarios (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id;",
                        (username, email, password_hash))
            user_id = cur.fetchone()[0]
            conn.commit()
            flash('Registro exitoso. Por favor, inicia sesión.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error al registrar usuario: {e}. El nombre de usuario o email ya existe.')
            if conn:
                conn.rollback()
        finally:
            if conn:
                cur.close()
                conn.close()
    return render_template('index.html', show_register=True)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, username, email, password_hash FROM Usuarios WHERE username = %s;", (username,))
            user_data = cur.fetchone()
            cur.close()
            
            if user_data and check_password_hash(user_data[3], password):
                user = User(id=user_data[0], username=user_data[1], email=user_data[2], password_hash=user_data[3])
                login_user(user)
                flash('Inicio de sesión exitoso.')
                return redirect(url_for('dashboard'))
            else:
                flash('Nombre de usuario o contraseña incorrectos.')
        except Exception as e:
            flash(f'Error al intentar iniciar sesión: {e}')
        finally:
            if conn:
                conn.close()
    return render_template('index.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.')
    return redirect(url_for('auth.login'))

def load_user(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password_hash FROM Usuarios WHERE id = %s;", (user_id,))
        user_data = cur.fetchone()
        cur.close()
        if user_data:
            return User(id=user_data[0], username=user_data[1], email=user_data[2], password_hash=user_data[3])
        return None
    except Exception as e:
        print(f"Error loading user: {e}")
        return None
    finally:
        if conn:
            conn.close()