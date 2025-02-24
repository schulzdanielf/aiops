CREATE DATABASE IF NOT EXISTS filmes_db;
USE filmes_db;

CREATE TABLE IF NOT EXISTS filmes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    ano_lancamento INT,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS atores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS filme_ator (
    filme_id INT,
    ator_id INT,
    FOREIGN KEY (filme_id) REFERENCES filmes(id),
    FOREIGN KEY (ator_id) REFERENCES atores(id),
    PRIMARY KEY (filme_id, ator_id)
);
