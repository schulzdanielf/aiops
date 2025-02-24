def load_movies():
    print("📊 Carregando filmes no MySQL...")
    
    # Verifica conexão com o MySQL
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ Erro ao conectar no MySQL: {e}")
        return

    # Caminho do arquivo de filmes
    titles_file = f"{DATA_DIR}/titles.tsv.gz"
    
    # Lista para armazenar os registros em lote
    batch = []
    batch_size = 1000  # Tamanho do lote para inserção em massa
    
    try:
        with gzip.open(titles_file, "rt", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            
            for row in reader:
                # Filtrar apenas filmes
                if row["titleType"] != "movie":
                    continue

                # Validar campos obrigatórios
                title = row["primaryTitle"]
                year = row["startYear"]
                genres = row["genres"]

                if not (title and year.isdigit() and genres != "\\N"):
                    continue
                
                # Converter ano para inteiro
                year = int(year)

                # Adicionar registro ao lote
                batch.append((title, year, genres))
                
                # Inserir lote no banco a cada 1000 registros
                if len(batch) >= batch_size:
                    cursor.executemany(
                        """
                        INSERT INTO filmes (titulo, ano_lancamento, descricao)
                        VALUES (%s, %s, %s)
                        """,
                        batch
                    )
                    conn.commit()
                    print(f"✅ {len(batch)} filmes carregados...")
                    batch.clear()
        
        # Inserir o restante dos registros
        if batch:
            cursor.executemany(
                """
                INSERT INTO filmes (titulo, ano_lancamento, descricao)
                VALUES (%s, %s, %s)
                """,
                batch
            )
            conn.commit()
            print(f"✅ {len(batch)} filmes finais carregados.")
        
    except Exception as e:
        print(f"❌ Erro ao processar filmes: {e}")
    finally:
        cursor.close()
        conn.close()

    print("🚀 Importação de filmes concluída com sucesso!")
