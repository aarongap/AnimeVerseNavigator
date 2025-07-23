import os
import psycopg2
from dotenv import load_dotenv

load_dotenv() # Carga las variables de entorno

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def execute_sql_file(filepath):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        with open(filepath, 'r') as f:
            cur.execute(f.read())
        conn.commit()
        cur.close()
        print(f"Executed SQL file: {filepath}")
    except Exception as e:
        print(f"Error executing {filepath}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Puedes ejecutar esto una vez para configurar tu DB
    # Asegúrate de que tu .env tenga la URL de tu DB
    print("Intentando conectar y ejecutar scripts de BD...")
    # Esto solo se ejecuta la primera vez para crear la BD y cargar datos
    # execute_sql_file('database/create_tables.sql')
    # execute_sql_file('database/functions_procedures.sql')
    # execute_sql_file('database/triggers.sql')
    # execute_sql_file('database/sample_data.sql')
    print("Scripts de BD ejecutados (o intentados).")

    # Ejemplo de uso de una función/procedimiento
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Ejemplo de llamada a función
        cur.execute("SELECT * FROM fn_obtener_animes_por_genero('fantasia')")
        print("\nAnimes de Fantasía:")
        for row in cur.fetchall():
            print(row)

        # Ejemplo de llamada a procedimiento (para registrar nuevo anime)
        # cur.execute("CALL sp_registrar_nuevo_anime(%s, %s, %s, %s, %s)",
        #             ('Nuevo Anime Test', 'Descripción de test', 2024, 'Studio Ghibli', ['Aventura', 'Drama']))
        # conn.commit()
        # print("\nProcedimiento sp_registrar_nuevo_anime ejecutado (si no estaba comentado).")

        # Demostración de trigger: Insertar reseña para Attack on Titan (anime_id: 1)
        # Primero, obtén un usuario_id y anime_id de sample_data.sql para probar
        # Por ejemplo, usuario_id 1 (juanito), anime_id 1 (Attack on Titan)
        # cur.execute("INSERT INTO Calificaciones_Reseñas (usuario_id, anime_id, calificacion, resena) VALUES (2, 1, 6, 'Una reseña de prueba para trigger.');")
        # conn.commit()
        # cur.execute("SELECT titulo, promedio_calificacion FROM Animes WHERE id = 1;")
        # print("\nPromedio de calificación de Attack on Titan después de nueva reseña (debería cambiar):", cur.fetchone())

        # Demostración de trigger de eliminación
        # Asegúrate de tener un anime que puedas eliminar para la prueba
        # cur.execute("DELETE FROM Animes WHERE titulo = 'Nuevo Anime Test';")
        # conn.commit()
        # cur.execute("SELECT * FROM Auditoria_Animes WHERE titulo_anime = 'Nuevo Anime Test';")
        # print("\nRegistro en Auditoria_Animes después de eliminar 'Nuevo Anime Test' (si existía):", cur.fetchone())

        cur.close()
    except Exception as e:
        print(f"Error en el ejemplo de uso: {e}")
    finally:
        if conn:
            conn.close()