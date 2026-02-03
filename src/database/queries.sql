
-- QUERY 1:
WITH trimestres_ordenados AS (
    SELECT
        d.cnpj,
        o.razao_social,
        d.ano,
        d.trimestre,
        d.valor_despesas,
        FIRST_VALUE(d.valor_despesas) OVER (
            PARTITION BY d.cnpj
            ORDER BY d.ano, d.trimestre
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as primeiro_valor,
        LAST_VALUE(d.valor_despesas) OVER (
            PARTITION BY d.cnpj
            ORDER BY d.ano, d.trimestre
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as ultimo_valor,
        COUNT(*) OVER (PARTITION BY d.cnpj) as qtd_trimestres
    FROM despesas d
    JOIN operadoras o ON d.cnpj = o.cnpj
    WHERE d.valor_despesas > 0
),
crescimento AS (
    SELECT DISTINCT
        cnpj,
        razao_social,
        primeiro_valor,
        ultimo_valor,
        qtd_trimestres,
        ROUND(
            ((ultimo_valor - primeiro_valor) / NULLIF(primeiro_valor, 0)) * 100,
            2
        ) as crescimento_percentual
    FROM trimestres_ordenados
    WHERE qtd_trimestres >= 2  -- Pelo menos 2 trimestres para comparar
)
SELECT
    razao_social as "Razão Social",
    primeiro_valor as "Despesa Inicial (R$)",
    ultimo_valor as "Despesa Final (R$)",
    crescimento_percentual as "Crescimento (%)",
    qtd_trimestres as "Trimestres Analisados"
FROM crescimento
ORDER BY crescimento_percentual DESC
LIMIT 5;



-- QUERY 2
SELECT
    o.uf as "UF",
    COUNT(DISTINCT d.cnpj) as "Qtd Operadoras",
    SUM(d.valor_despesas) as "Total Despesas (R$)",
    ROUND(AVG(d.valor_despesas), 2) as "Média por Registro (R$)",
    ROUND(
        SUM(d.valor_despesas) / NULLIF(COUNT(DISTINCT d.cnpj), 0),
        2
    ) as "Média por Operadora (R$)"
FROM despesas d
JOIN operadoras o ON d.cnpj = o.cnpj
WHERE o.uf IS NOT NULL
GROUP BY o.uf
ORDER BY SUM(d.valor_despesas) DESC
LIMIT 5;


-- QUERY 3
WITH media_geral AS (
    -- Calcula média geral de todas as despesas
    SELECT AVG(valor_despesas) as media
    FROM despesas
),
trimestres_acima_media AS (
    -- Para cada operadora/trimestre, verifica se está acima da média
    SELECT
        d.cnpj,
        o.razao_social,
        d.ano,
        d.trimestre,
        d.valor_despesas,
        mg.media,
        CASE
            WHEN d.valor_despesas > mg.media THEN 1
            ELSE 0
        END as acima_media
    FROM despesas d
    JOIN operadoras o ON d.cnpj = o.cnpj
    CROSS JOIN media_geral mg
),
contagem_por_operadora AS (
    -- Conta quantos trimestres cada operadora ficou acima da média
    SELECT
        cnpj,
        razao_social,
        SUM(acima_media) as trimestres_acima_media,
        COUNT(*) as total_trimestres
    FROM trimestres_acima_media
    GROUP BY cnpj, razao_social
)
SELECT
    razao_social as "Razão Social",
    trimestres_acima_media as "Trimestres Acima da Média",
    total_trimestres as "Total de Trimestres"
FROM contagem_por_operadora
WHERE trimestres_acima_media >= 2
ORDER BY trimestres_acima_media DESC, razao_social;

-- Justificativa (documentar no DECISOES.md):
-- Opção escolhida: CTEs (Common Table Expressions)
-- Alternativas consideradas:
--   - Subqueries aninhadas: Menos legível, difícil manutenção
--   - Tabela temporária: Overhead desnecessário para query pontual
--   - Window function única: Possível mas menos clara
-- Trade-off: Performance similar, mas CTEs são muito mais legíveis
-- Facilita debug (pode executar cada CTE separadamente)
-- Melhor para time que vai manter o código
