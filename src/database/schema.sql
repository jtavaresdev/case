CREATE TABLE operadoras (
    cnpj VARCHAR(14) PRIMARY KEY,
    registro_ans VARCHAR(20) UNIQUE NOT NULL,
    razao_social VARCHAR(255) NOT NULL,
    modalidade VARCHAR(100),
    uf CHAR(2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE despesas (
    id SERIAL PRIMARY KEY,
    cnpj VARCHAR(14) NOT NULL REFERENCES operadoras(cnpj),
    ano INTEGER NOT NULL,
    trimestre INTEGER NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
    valor_despesas NUMERIC(15, 2) NOT NULL,
    descricao VARCHAR(400),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id)
);

CREATE TABLE despesas_agregadas (
    id SERIAL PRIMARY KEY,
    razao_social VARCHAR(255) NOT NULL,
    uf CHAR(2),
    total_despesas NUMERIC(15, 2),
    media_por_trimestre NUMERIC(15, 2),
    desvio_padrao NUMERIC(15, 2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
