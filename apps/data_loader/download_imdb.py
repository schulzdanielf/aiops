import pymysql
import requests
import gzip
import csv
import os
import time

# URLs dos datasets do IMDb
IMDB_DATASETS = {
    "titles": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "crew": "https://datasets.imdbws.com/title.principals.tsv.gz",
    "names": "https://datasets.imdbws.com/name.basics.tsv.gz",
}

# Diretório para armazenar os arquivos
DATA_DIR = "/app/data_loader/imdb_data"

# Aguarda o MySQL estar disponível
def wait_for_mysql():
    for _ in range(30):
        try:
            conn = pymysql.connect(
                host="0.0.0.0",
                user="root",
                password="senha123"
            )
            print("✅ MySQL disponível!")
            conn.close()
            return
        except Exception as e:
            print(e)
            print("⏳ Aguardando MySQL...")
            time.sleep(10)
    raise TimeoutError("❌ Timeout ao conectar no MySQL.")

# Função para baixar os arquivos
def download_imdb_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    for key, url in IMDB_DATASETS.items():
        local_file = f"{DATA_DIR}/{key}.tsv.gz"
        print(f"⬇️ Baixando {key}...")
        response = requests.get(url, stream=True)
        with open(local_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Download de {key} concluído.")

# Função para conectar ao MySQL
def get_connection():
    return pymysql.connect(
        host="0.0.0.0",
        user="root",
        password="senha123",
        database="filmes_db"
    )

# Cria as tabelas no MySQL
def create_schema():
    with get_connection() as conn:
        with conn.cursor() as cur:
            with open("/app/data_loader/schema.sql", "r") as f:
                cur.execute(f.read())
        conn.commit()
    print("✅ Esquema do banco criado com sucesso.")

# Função para converter '\N' para None
def convert_null(value):
    return None if value == '\\N' else value

# Função para carregar os filmes
def load_movies():
    print("📊 Carregando filmes no MySQL...")
    with get_connection() as conn:
        with conn.cursor() as cur:
            with open("apps/data_loader/imdb_data/titles.tsv", "r") as f:
                reader = csv.DictReader(f, delimiter="\t")
                reader = list(reader)[:10000]
                for row in reader:
                    if row["titleType"] == "movie":
                        start_year = convert_null(row["startYear"])  # Trata '\N'
                        duration = convert_null(row["runtimeMinutes"])  # Trata '\N'
                        cur.execute(
                            """
                            INSERT INTO filmes (titulo, ano_lancamento, genero, duracao_minutos, tconst)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (row["primaryTitle"], start_year, row["genres"], duration, row["tconst"])
                        )
        conn.commit()
    print("✅ Filmes carregados com sucesso.")

# Função para carregar atores
def load_actors():
    print("🎭 Carregando atores no MySQL...")
    actor_ids = set()
    with gzip.open(f"{DATA_DIR}/crew.tsv.gz", "rt") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            actor_ids.add(row["nconst"])

    with get_connection() as conn:
        with conn.cursor() as cur:
            with gzip.open(f"{DATA_DIR}/names.tsv.gz", "rt") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    if row["nconst"] in actor_ids:
                        cur.execute(
                            """
                            INSERT INTO atores (nome)
                            VALUES (%s)
                            """,
                            (row["primaryName"],)
                        )
        conn.commit()
    print("✅ Atores carregados com sucesso.")

if __name__ == "__main__":
    wait_for_mysql()
    # download_imdb_files()
    # create_schema()
    load_movies()
    # load_actors()
    print("🚀 Importação concluída com sucesso!")
