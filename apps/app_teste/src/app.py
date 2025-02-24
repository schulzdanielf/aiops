from flask import Flask, jsonify, request
import pymysql
from load_movies import load_movies

app = Flask(__name__)

# Configurações do MySQL
MYSQL_CONFIG = {
    "host": "mysql",
    "user": "root",
    "password": "senha123",
    "database": "filmes_db",
    "port": 3306
}

# Conexão com o banco de dados
def get_connection():
    return pymysql.connect(**MYSQL_CONFIG, cursorclass=pymysql.cursors.DictCursor)

# Rota de saúde
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# Rota para importar filmes do IMDB
@app.route("/import", methods=["POST"])
def import_movies():
    try:
        load_movies()  # Executa a importação
        return jsonify({"message": "Importação iniciada com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para listar filmes com filtros
@app.route("/movies", methods=["GET"])
def get_movies():
    try:
        title = request.args.get("title")
        genre = request.args.get("genre")
        actor = request.args.get("actor")

        query = "SELECT * FROM filmes WHERE 1=1"
        params = []

        if title:
            query += " AND titulo LIKE %s"
            params.append(f"%{title}%")

        if genre:
            query += " AND descricao LIKE %s"
            params.append(f"%{genre}%")

        # Ajustar caso implemente a relação de atores
        if actor:
            query += " AND atores LIKE %s"
            params.append(f"%{actor}%")

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            movies = cursor.fetchall()

        return jsonify(movies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# Rota para recomendar filmes
@app.route("/recommendations", methods=["GET"])
def get_recommendations():
    try:
        recent_movie = request.args.get("recent_movie")

        if not recent_movie:
            return jsonify({"error": "Parâmetro 'recent_movie' é obrigatório"}), 400

        conn = get_connection()
        with conn.cursor() as cursor:
            # Buscar o gênero do último filme assistido
            cursor.execute("SELECT descricao FROM filmes WHERE titulo = %s LIMIT 1", (recent_movie,))
            movie = cursor.fetchone()

            if not movie:
                return jsonify({"error": "Filme não encontrado"}), 404

            genre = movie["descricao"].split(",")[0]

            # Buscar recomendações no mesmo gênero
            cursor.execute(
                "SELECT * FROM filmes WHERE descricao LIKE %s AND titulo != %s LIMIT 5",
                (f"%{genre}%", recent_movie)
            )
            recommendations = cursor.fetchall()

        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# Inicializar a aplicação Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
