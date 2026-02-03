# Teste Técnico - Análise de Dados ANS

Sistema completo de ETL, análise e visualização de dados de operadoras de saúde da ANS (Agência Nacional de Saúde Suplementar).

## Estrutura do Projeto

```
case/
├── dados/
│   ├── raw/                    # Dados brutos baixados
│   ├── extracted/              # Arquivos extraídos dos ZIPs
│   └── output/                 # CSVs processados
├── src/
│   ├── data/                   # Scripts de ETL (Item 1 e 2)
│   │   ├── extractor.py
│   │   ├── processor.py
│   │   ├── validator.py
│   │   └── aggregator.py
│   ├── database/               # SQL e banco de dados (Item 3)
│   │   ├── schema.sql
│   │   ├── import_data.sql
│   │   └── queries.sql
│   └── api/                    # Backend FastAPI (Item 4)
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models/
│       └── routes/
├── frontend/                   # Interface Vue.js (Item 4)
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── scripts/                    # Scripts auxiliares
│   ├── setup_database.sh
│   └── run_queries.sh
├── docker-compose.yml
├── requirements.txt
└── README.md
```
---

## Instalação

### 1. Clone e configure ambiente Python

```bash
# Clone o repositório (ou descompacte o ZIP)
cd case

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt
```

### 2. Configure variáveis de ambiente

Crie arquivo `.env` na raiz:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ans_database
DB_USER=ans_user
DB_PASSWORD=ans_pass123
```
---
## Execução

### Parte 1 e 2: ETL de Dados

```bash 
python src/data/extractor.py
python src/data/processor.py
```

Os dados processados estarão em:
- `dados/output/consolidado_despesas.csv`
- `dados/output/despesas_agregadas.csv`

### Parte 3: Banco de Dados

#### 3.1. Iniciar PostgreSQL

```bash
docker-compose up -d
```

#### 3.2. Criar schema

```bash
docker exec -i ans_postgres psql -U ans_user -d ans_database < src/database/schema.sql
```

#### 3.3. Importar dados

```bash
docker exec -i ans_postgres psql -U ans_user -d ans_database < src/database/import_data.sql
```

#### 3.4. Executar queries analíticas

```bash
docker exec -i ans_postgres psql -U ans_user -d ans_database < src/database/queries.sql
```

### Parte 4: API e Frontend

#### 4.1. Iniciar API (Terminal 1)

```bash
# Da raiz do projeto
source venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a documentação: http://localhost:8000/docs

#### 4.2. Iniciar Frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Acesse a aplicação: http://localhost:3000

---

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/operadoras` | Lista operadoras (paginado) |
| GET | `/api/operadoras/{cnpj}` | Detalhes de uma operadora |
| GET | `/api/operadoras/{cnpj}/despesas` | Histórico de despesas |
| GET | `/api/estatisticas` | Estatísticas agregadas |
| GET | `/health` | Health check |

### Postman link

https://web.postman.co/workspace/My-Workspace~f1262ed3-1576-43a0-8620-74f47a5206db/collection/42243386-740a205a-0d9e-4c94-90f0-6d707662f8d6?action=share&source=copy-link&creator=42243386

### Exemplos de uso

```bash
# Listar operadoras
curl "http://localhost:8000/api/operadoras?page=1&limit=20"

# Buscar por nome
curl "http://localhost:8000/api/operadoras?search=unimed"

# Detalhes de uma operadora
curl "http://localhost:8000/api/operadoras/12345678901234"

# Estatísticas
curl "http://localhost:8000/api/estatisticas"
```

---

## Queries Analíticas e Trade-Off 

Estão detalhados no documento DECISOES.md

### Frontend

**Framework:** Vue 3 + Vite  
**Busca:** Híbrida (servidor + cliente)  
**Estado:** Composables (sem Pinia)  
**Performance:** Paginação (20 itens/página)

---
## Testes

### Verificar API

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Verificar Banco

```bash
docker exec -it ans_postgres psql -U ans_user -d ans_database -c "\dt"
```

Deve listar 3 tabelas:
- operadoras
- despesas
- despesas_agregadas

---

## Parar os serviços

```bash
# Parar API: Ctrl+C no terminal

# Parar Frontend: Ctrl+C no terminal

# Parar PostgreSQL
docker-compose down

# Parar e remover volumes (apaga dados)
docker-compose down -v
```

---

## Estrutura dos Dados

### Tabela: operadoras

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| cnpj | VARCHAR(14) | CNPJ (chave primária) |
| registro_ans | VARCHAR(20) | Registro ANS |
| razao_social | VARCHAR(255) | Razão social |
| modalidade | VARCHAR(100) | Modalidade |
| uf | CHAR(2) | Estado |

### Tabela: despesas

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | SERIAL | ID (chave primária) |
| cnpj | VARCHAR(14) | CNPJ da operadora |
| ano | INTEGER | Ano |
| trimestre | INTEGER | Trimestre (1-4) |
| valor_despesas | NUMERIC(15,2) | Valor em reais |
| descricao | VARCHAR(400) | Descrição |

---

## Documentação Adicional

- **DECISOES.md**: Justificativas detalhadas de trade-offs técnicos
- **API Docs**: http://localhost:8000/docs (quando API estiver rodando)
- **Queries SQL**: `src/database/queries.sql`

---

## Licença

Este projeto foi desenvolvido como parte de um teste técnico.
