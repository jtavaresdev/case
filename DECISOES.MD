# Decisões Técnicas

## Escolha da Linguagem: Python

Utilizei Python devido a dois motivos principais:

1. **Manipulação de dados**: Ecossistema robusto (Pandas)
2. **Requisito do projeto**: Necessidade de utilizar Python no item 4.2 (API)

---
# 1. TESTE DE INTEGRAÇÃO COM API PÚBLICA

## 1.2 Processamento de Arquivos

### Trade-off: Processamento em memória vs. incremental

**Decisão:** Processar todos os arquivos em memória

**Justificativa:**
- Maior velocidade de processamento
- Única escrita no disco (evita erros de buffer)
- Volume de dados (~8MB por arquivo) comporta processamento em memória

**Fluxo implementado:**
1. Ler arquivos .csv
2. Extrair rows que possuem dados de EVENTOS/SINISTROS
3. Criar novo CSV com esses dados consolidados

---

## 1.3 Consolidação e Análise de Inconsistências

### Tratamento de dados ausentes

**CNPJ ausente:**
- Dados originais possuem apenas RegistroANS
- JOIN posterior com arquivo cadastral (item 2.2) para obter CNPJ

### Valores negativos e zerados
**Decisão:** Manter valores negativos e zerados

**Justificativa:**
- Valores zerados: Indicam ausência de movimentação no período
- Armazenar contadores para análise posterior
---

# 2. TESTE DE TRANSFORMAÇÃO E VALIDAÇÃO DE DADOS

## Arquitetura de validação

**Decisão:** Criar classe `DataValidator` separada

**Justificativa:**
- Modularização: Facilita refatoração futura
- Separação de responsabilidades
- Classe `DataProcessor` mantém foco em transformação de dados

---

## 2.1 Validação de Dados

### Trade-off: Rejeitar vs. armazenar dados inválidos

**Decisão:** Armazenar dados inválidos em arquivo separado

**Implementação:**
- CNPJs inválidos → `cnpjs_invalidos.csv`
- Dados inconsistentes do tipo string → Marcados como "PENDENTE"

**Justificativa:**
- Rastreabilidade: Permite análise posterior de dados rejeitados
---

## 2.2 Enriquecimento de Dados

### Trade-off: Join manual vs. método nativo do Pandas

**Decisão:** Utilizar `DataFrame.merge()` (método nativo do Pandas)

**Implementação:**
```python
def join_registro_ans(df_principal, df_registro_ans, ...):
    return df_principal.merge(df_registro_ans, left_on=..., right_on=..., how='left')
```
**Justificativa:**
- Performance adequada para o volume de dados (~100k registros)
- Menor complexidade de manutenção

---

# 3. TESTE DE BANCO DE DADOS E ANÁLISE

## 3.2 Estrutura de Tabelas

### 3.2.1 Trade-off: Normalização vs. Desnormalização

**Decisão:** Abordagem HÍBRIDA

**Estrutura implementada:**
- **Normalizadas (3FN):** `operadoras`, `despesas`
- **Desnormalizada:** `despesas_agregadas`

**Justificativa:**
- Normalização: Mantém integridade referencial e facilita atualizações
- Desnormalização (agregados): Performance em queries analíticas
---

### 3.2.2 Trade-off: Tipos de dados

**Valores monetários: `NUMERIC(15,2)`**

**Justificativa:**
- Precisão exata (sem erro de arredondamento do FLOAT)
- Padrão SQL para valores financeiros
- Suporta até 999 trilhões com 2 casas decimais

**Datas: `INTEGER` (ano) + `INTEGER` (trimestre)**

**Justificativa:**
- Dados originais já vêm nessa granularidade
- Queries simples: `WHERE ano = 2025 AND trimestre = 1`
- Não requer parsing/conversão
---
## 3.3 Importação de Dados

**Tratamento de inconsistências:**
Durante o processamento em Python (itens 1 e 2), inconsistências foram tratadas previamente:
- Conversão de valores monetários (vírgula → ponto)
- Validação de CNPJs
- Normalização de trimestres/anos
**Comando de importação:**
```bash
docker exec -i ans_postgres psql -U ans_user -d ans_database < src/database/import_data.sql
```
---

## 3.4 Queries Analíticas

### Query 3: Trade-off de abordagem

**Decisão:** CTEs (Common Table Expressions)

**Estrutura:**
1. `media_geral`: Calcula média única
2. `trimestres_acima_media`: Marca cada trimestre
3. `contagem_por_operadora`: Agrega resultados
4. SELECT final: Filtra operadoras com 2+ trimestres acima da média

**Justificativa:**
- **Legibilidade:** Código lê como sequência lógica
- **Performance:** PostgreSQL otimiza CTEs automaticamente

---

# 4. TESTE DE API E INTERFACE WEB

## 4.2 Backend

### 4.2.1 Trade-off: Flask vs. FastAPI

**Decisão:** FastAPI
**Justificativa:**
1. **Velocidade de implementação:** 
2. **Performance:** 
3. **Documentação automática:** 

---

### 4.2.2 Estratégia de Paginação

**Decisão:** Offset-based

**Justificativa:**
- Facilidade de implementação
- Volume de dados relativamente pequeno (~1110 operadoras)
- Adequado para interface web com navegação por páginas
---

### 4.2.3 Cache vs. Queries Diretas

**Decisão:** Cache com TTL de 30 minutos para `/api/estatisticas`

**Justificativa:**
- **Performance:** Estatísticas gerais são custosas de calcular
- **Consistência:** Dados atualizados trimestralmente (baixa frequência)
- **Simplicidade:** Implementação direta com cache em memória

**Endpoints sem cache:**
- `/api/operadoras`: Dados específicos variam por busca/filtro
- `/api/operadoras/{cnpj}/despesas`: Consultas específicas

---

## 4.3 Frontend

### 4.3.1 Estratégia de Busca/Filtro

**Decisão:** Híbrida (servidor + cliente)

**Implementação:**
- Busca inicial: Servidor (endpoint com parâmetro `search`)
- Cache: Dados já carregados permanecem no cliente
