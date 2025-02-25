from flask import Flask, jsonify, request, json, Response
from flask_restx import Api, Resource, fields
import pymysql
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor
import psutil
import time


# Configuração do OpenTelemetry Metrics
metric_exporter = OTLPMetricExporter(endpoint="http://otelcol:4317/v1/metrics", insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=15000)

# Configuração do MeterProvider com o MetricReader
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
meter = metrics.get_meter("filmes_meter", "0.1.0")

# Definição de métricas
filmes_pesquisados_counter = meter.create_counter(
    "filmes_pesquisados",
    description="Contagem de filmes pesquisados",
    unit="1",
)

requests_counter = meter.create_counter(
    "requests_total",
    description="Tráfego de Requisições",
    unit="1",
)

errors_counter = meter.create_counter(
    "errors_total",
    description="Quantidade de requisições diferentes de 200",
    unit="1",
)

latency = meter.create_histogram(
    "latency",
    description="Latência das requisições",
    unit="ms"
)

# Instrumentar o PyMySQL
PyMySQLInstrumentor().instrument()

app = Flask(__name__)
api = Api(app, version='1.0', title='API de Filmes', description='API para gerenciar filmes')

# Instrumentar métricas do sistema
SystemMetricsInstrumentor().instrument()

# Instrumentar o Flask
FlaskInstrumentor().instrument_app(app)


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
        requests_counter.add(1)
        start_time = time.time()
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

            # Incrementar a métrica de filmes pesquisados
            filmes_pesquisados_counter.add(len(movies), {"endpoint": "/movies"})
            # Calcular a latência
            latency.record((time.time() - start_time) * 1000)

            return movies, 200

        except Exception as e:
            errors_counter.add(1)
            print(f"Erro ao buscar filmes: {e}")
            message = json.dumps({'Error interno': str(e)})
            return Response(message, status=500, mimetype='application/json')


@app.errorhandler(404)
def page_not_found(e):
    errors_counter.add(1)
    print(f"Erro 404: Página não encontrada - {e}")
    message = json.dumps({"error": "Página não encontrada"})
    return Response(message, status=404, mimetype='application/json')


# Executar a aplicação
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
