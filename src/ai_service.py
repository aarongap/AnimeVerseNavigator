import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import random
from src.database import get_db_connection

class AnimeRecommender:
    def __init__(self):
        self.animes_data = self._load_animes_data()
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        if self.animes_data:
            self._train_recommender()

    def _load_animes_data(self):
        """Carga los animes y sus géneros desde la base de datos."""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    A.id,
                    A.titulo,
                    A.descripcion,
                    STRING_AGG(G.nombre_genero, ', ') AS generos
                FROM Animes A
                LEFT JOIN Animes_Generos AG ON A.id = AG.anime_id
                LEFT JOIN Generos G ON AG.genero_id = G.id
                GROUP BY A.id, A.titulo, A.descripcion
                ORDER BY A.id;
            """)
            animes = cur.fetchall()
            cur.close()
            return animes
        except Exception as e:
            print(f"Error al cargar datos de animes para el recomendador: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _train_recommender(self):
        """Entrena el recomendador TF-IDF basado en la descripción y géneros."""
        if not self.animes_data:
            print("No hay datos de animes para entrenar el recomendador.")
            return

        corpus = []
        for anime in self.animes_data:
            # Combinar descripción y géneros para el corpus
            combined_text = f"{anime[2] or ''} {anime[3] or ''}"
            corpus.append(combined_text)

        if corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            print("Recomendador de IA entrenado exitosamente.")
        else:
            print("Corpus vacío, no se pudo entrenar el recomendador.")

    def get_recommendations(self, user_id, num_recommendations=5):
        """
        Obtiene recomendaciones personalizadas para un usuario.
        Lógica "IA": Basado en animes que el usuario ha calificado alto
        y animes no vistos con géneros/descripciones similares.
        """
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # 1. Obtener animes que el usuario ha visto/calificado alto
            cur.execute("""
                SELECT DISTINCT A.id, A.titulo
                FROM Calificaciones_Reseñas CR
                JOIN Animes A ON CR.anime_id = A.id
                WHERE CR.usuario_id = %s AND CR.calificacion >= 7;
            """, (user_id,))
            user_rated_animes = cur.fetchall()

            # 2. Obtener todos los animes que el usuario ya ha visto o tiene en su lista
            cur.execute("""
                SELECT anime_id FROM Lista_Ver WHERE usuario_id = %s
                UNION
                SELECT anime_id FROM Calificaciones_Reseñas WHERE usuario_id = %s;
            """, (user_id, user_id))
            watched_anime_ids = {row[0] for row in cur.fetchall()}

            recommended_animes = []
            if not self.tfidf_matrix is None and self.animes_data:
                # Encontrar los índices de los animes que el usuario calificó alto
                user_rated_anime_indices = [
                    i for i, anime_db in enumerate(self.animes_data)
                    if anime_db[0] in {a[0] for a in user_rated_animes}
                ]

                if user_rated_anime_indices:
                    # Calcular la similitud del coseno entre los animes calificados y todos los demás
                    user_profile_vector = self.tfidf_matrix[user_rated_anime_indices].mean(axis=0)
                    cosine_sim = cosine_similarity(user_profile_vector, self.tfidf_matrix)
                    sim_scores = list(enumerate(cosine_sim[0]))

                    # Ordenar los animes por puntuación de similitud
                    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

                    for i, score in sim_scores:
                        anime_id = self.animes_data[i][0]
                        anime_title = self.animes_data[i][1]
                        if anime_id not in watched_anime_ids and anime_id not in {a['id'] for a in recommended_animes}:
                            recommended_animes.append({'id': anime_id, 'titulo': anime_title, 'score': score})
                            if len(recommended_animes) >= num_recommendations:
                                break
            
            # Si no hay suficientes recomendaciones o no hay datos de usuario, añadir aleatorios
            if len(recommended_animes) < num_recommendations:
                cur.execute("""
                    SELECT id, titulo FROM Animes
                    WHERE id NOT IN (
                        SELECT anime_id FROM Lista_Ver WHERE usuario_id = %s
                        UNION
                        SELECT anime_id FROM Calificaciones_Reseñas WHERE usuario_id = %s
                    )
                    ORDER BY RANDOM() LIMIT %s;
                """, (user_id, user_id, num_recommendations - len(recommended_animes)))
                random_animes = cur.fetchall()
                for r_id, r_title in random_animes:
                    if r_id not in {a['id'] for a in recommended_animes}:
                        recommended_animes.append({'id': r_id, 'titulo': r_title, 'score': 0}) # Score 0 para aleatorios

            cur.close()
            return recommended_animes[:num_recommendations]

        except Exception as e:
            print(f"Error al obtener recomendaciones para el usuario {user_id}: {e}")
            return []
        finally:
            if conn:
                conn.close()

if __name__ == '__main__':
    # Pequeña demostración de la clase de recomendación
    recommender = AnimeRecommender()
    print("\nRecomendaciones para el usuario 1 (juanito):")
    recs = recommender.get_recommendations(user_id=1)
    for r in recs:
        print(f"- {r['titulo']} (ID: {r['id']}, Score: {r['score']:.2f})")

    print("\nRecomendaciones para el usuario 2 (mariaperez):")
    recs = recommender.get_recommendations(user_id=2)
    for r in recs:
        print(f"- {r['titulo']} (ID: {r['id']}, Score: {r['score']:.2f})")