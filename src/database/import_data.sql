
TRUNCATE TABLE despesas CASCADE;
TRUNCATE TABLE operadoras CASCADE;
TRUNCATE TABLE despesas_agregadas CASCADE;

CREATE TEMP TABLE temp_operadora(
    registro_operadora VARCHAR(50),
    cnpj VARCHAR(20),
    razao_social TEXT,
    nome_fantasia TEXT,
    modalidade VARCHAR(100),
    logradouro TEXT,
    numero VARCHAR(50),
    complemento TEXT,
    bairro TEXT,
    cidade TEXT,
    uf CHAR(2),
    cep VARCHAR(20),
    ddd VARCHAR(10),
    telefone VARCHAR(50),
    fax VARCHAR(50),
    endereco_eletronico TEXT,
    representante TEXT,
    cargo_representante TEXT,
    regiao_comercializacao TEXT,
    data_registro_ans DATE
);

COPY temp_operadora
FROM '/csv_data/raw/Relatorio_cadop.csv'
DELIMITER ';'
CSV HEADER
ENCODING 'UTF8';

INSERT INTO operadoras(cnpj, registro_ans, razao_social, modalidade, uf)
SELECT DISTINCT
    REGEXP_REPLACE(TRIM(p.cnpj), '[^0-9]', '', 'g') as cnpj_limpo,
    TRIM(p.registro_operadora) as registro_ans,
    TRIM(p.razao_social) as razao_social,
    TRIM(p.modalidade) as modalidade,
    TRIM(p.uf) as uf
FROM temp_operadora p
WHERE
    p.cnpj IS NOT NULL
    AND TRIM(p.cnpj) != ''
    AND LENGTH(REGEXP_REPLACE(TRIM(p.cnpj), '[^0-9]', '', 'g')) = 14;

DROP TABLE temp_operadora;

CREATE TEMP TABLE temp_despesas (
    registro_ans VARCHAR(50),
    cnpj VARCHAR(20),
    razao_social TEXT,
    trimestre INTEGER,
    ano INTEGER,
    valor_despesas NUMERIC(15,2),
    modalidade VARCHAR(100),
    uf CHAR(2),
    descricao TEXT
);

COPY temp_despesas
FROM '/csv_data/output/consolidado_despesas.csv'
DELIMITER ';'
CSV HEADER
ENCODING 'UTF8';


INSERT INTO despesas (cnpj, ano, trimestre, valor_despesas, descricao)
SELECT
    t.cnpj,
    t.ano,
    t.trimestre,
    COALESCE(t.valor_despesas, 0),
    TRIM(t.descricao) as descricao
FROM temp_despesas t
WHERE EXISTS (
    SELECT 1
    FROM operadoras o
    WHERE o.cnpj = t.cnpj
)
AND t.cnpj IS NOT NULL
AND t.cnpj != 'PENDENTE'
AND LENGTH(t.cnpj) = 14
AND t.ano IS NOT NULL
AND t.trimestre BETWEEN 1 AND 4
AND t.valor_despesas IS NOT NULL
AND t.valor_despesas >= 0;


DROP TABLE temp_despesas;

INSERT INTO despesas_agregadas (razao_social, uf, total_despesas, media_por_trimestre, desvio_padrao)
SELECT
    o.razao_social,
    o.uf,
    SUM(d.valor_despesas) as total_despesas,
    AVG(d.valor_despesas) as media_por_trimestre,
    STDDEV(d.valor_despesas) as desvio_padrao
FROM despesas d
JOIN operadoras o ON d.cnpj = o.cnpj
GROUP BY o.razao_social, o.uf;
