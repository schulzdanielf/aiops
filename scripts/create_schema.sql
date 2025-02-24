CREATE DATABASE filmes_db;
USE filmes_db;

-- Crie a tabela de filmes caso ela não exista
CREATE TABLE IF NOT EXISTS filmes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    genero TEXT,
    ano_lancamento INT,
    duracao_minutos INT,
    tconst VARCHAR(45) NOT NULL,
);


-- Tabela de Atores
CREATE TABLE IF NOT EXISTS atores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) UNIQUE NOT NULL
);

-- Relação Filme <-> Ator (N:N)
CREATE TABLE IF NOT EXISTS filme_ator (
    filme_id INT,
    ator_id INT,
    PRIMARY KEY (filme_id, ator_id),
    FOREIGN KEY (filme_id) REFERENCES filmes(id) ON DELETE CASCADE,
    FOREIGN KEY (ator_id) REFERENCES atores(id) ON DELETE CASCADE
);

-- Histórico de Filmes Assistidos (para Recomendação)
CREATE TABLE IF NOT EXISTS historico_assistidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    filme_id INT,
    assistido_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filme_id) REFERENCES filmes(id) ON DELETE CASCADE
);
