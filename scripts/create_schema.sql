CREATE DATABASE filmes_db;
USE filmes_db;

-- Tabela de Filmes
CREATE TABLE filmes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    ano_lancamento INT,
    duracao_minutos INT,
    classificacao VARCHAR(10), -- Ex: 12, 16, 18 anos
    poster_url TEXT
);

-- Tabela de Gêneros (Um filme pode ter vários gêneros)
CREATE TABLE generos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL
);

-- Relação Filme <-> Gênero (N:N)
CREATE TABLE filme_genero (
    filme_id INT,
    genero_id INT,
    PRIMARY KEY (filme_id, genero_id),
    FOREIGN KEY (filme_id) REFERENCES filmes(id) ON DELETE CASCADE,
    FOREIGN KEY (genero_id) REFERENCES generos(id) ON DELETE CASCADE
);

-- Tabela de Atores
CREATE TABLE atores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) UNIQUE NOT NULL
);

-- Relação Filme <-> Ator (N:N)
CREATE TABLE filme_ator (
    filme_id INT,
    ator_id INT,
    PRIMARY KEY (filme_id, ator_id),
    FOREIGN KEY (filme_id) REFERENCES filmes(id) ON DELETE CASCADE,
    FOREIGN KEY (ator_id) REFERENCES atores(id) ON DELETE CASCADE
);

-- Histórico de Filmes Assistidos (para Recomendação)
CREATE TABLE historico_assistidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    filme_id INT,
    assistido_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filme_id) REFERENCES filmes(id) ON DELETE CASCADE
);
