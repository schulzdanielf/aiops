from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
import pymysql

app = Flask(__name__)
api = Api(app, version='1.0', title='API de Filmes', description='API para gerenciar filmes')

# Configurações do MySQL
MYSQL_CONFIG = {
    "host": "mysql",
    "user": "root",
    "password": "senha123",
    "database": "filmes_db",
    "port": 3306
}

# Função para conectar ao banco de dados
def get_connection():
    return pymysql.connect(**MYSQL_CONFIG, cursorclass=pymysql.cursors.DictCursor)

# Swagger Model
movie_model = api.model('Movie', {
    'id': fields.Integer(description='ID do Filme'),
    'titulo': fields.String(description='Título do Filme'),
    'ano_lancamento': fields.Integer(description='Ano de Lançamento'),
    'genero': fields.String(description='Gênero do Filme'),
    'duracao_minutos': fields.Integer(description='Duração em Minutos'),
    'tconst': fields.String(description='Código Tconst')
})

# Rota de saúde
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# Endpoint para listar filmes com filtros
@api.route('/movies')
class MoviesList(Resource):
    """Listar filmes com filtros opcionais"""
    @api.doc(params={
        'id': 'ID do Filme',
        'title': 'Título do Filme',
        'year': 'Ano de Lançamento',
        'genero': 'Gênero do Filme',
        'tconst': 'Código Tconst do Filme'
    })
    def get(self):
        try:
            # Captura os parâmetros da URL
            movie_id = request.args.get("id")
            title = request.args.get("title")
            year = request.args.get("year")
            genero = request.args.get("genero")
            tconst = request.args.get("tconst")

            query = "SELECT * FROM filmes WHERE 1=1"
            params = []

            # Aplicar os filtros dinamicamente
            if movie_id:
                query += " AND id = %s"
                params.append(movie_id)

            if title:
                query += " AND titulo LIKE %s"
                params.append(f"%{title}%")

            if year:
                query += " AND ano_lancamento = %s"
                params.append(year)

            if genero:
                query += " AND genero LIKE %s"
                params.append(f"%{genero}%")

            if tconst:
                query += " AND tconst = %s"
                params.append(tconst)

            # Executar a consulta
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                movies = cursor.fetchall()

            return movies, 200

        except Exception as e:
            print(f"Erro ao buscar filmes: {e}")
            return jsonify({"error": "Erro interno no servidor"}), 500
        finally:
            if conn:
                conn.close()

# Executar a aplicação
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
