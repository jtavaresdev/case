# Decisoẽs técnicas
 Utilizei Python devido a dois motivos.
1. Manipulação de dados / Ecossistema Python
2. Mais adiante necessidade de utilizar Python pela descrição item 4.2

# 1. TESTE DE INTEGRAÇÃO COM API PÚBLICA
## 1.2. Processamente de Arquivos
### Trade-Off
Decidir processar todos os arquivos em memória devido 
a velocidade e fazer apenas uma escrita, evitando talvez
erros de escrita no buffer.

1. Ler arquivos .csv 
2. Extrair rows que possuem dados de EVENTOS/SINISTROS 
3. Criar novo CSV com esses dados.

## 1.3
Dados sem "CNPJ" apenas RegistoANS; entretanto mais adiante no case
é necessário fazer um JOIN e pegar CNPJ.

Sobre as inconsistencias como valores negativos e zerados vou manter,
entretanto, vou somar eles para ter essa informação.

# 2. TESTE DE TRANSFORMAÇÃO E VALIDAÇÃO DE DADOS
Tinha feito um validador na classe DataProcessor,
entretanto como vou verificar os CNPJs decidi modularizar 
e criar uma classe específica para isso, pois caso
mude a lógica de négocio seja fácil de refatorar.
### 2.1 Trade-Off
Decidi armazenar todo os dados, para os CNPJs inválidos,
decidi criar outro arquivo .csv para persistir esses dados inválidos.
Alias, todos os dados do tipo str na tabela que forem inconsistentes
vou persistir como "PENDENTE" para depois poder fazer analises
## 2.2 Trade-Off
Para o Join decidi criar uma função ´join_registro_ans´ utilizando
metodos nativos do pandas para faer um "left join"
Decidi utilizar metodos nativos para manter o padrão e que, ainda é 
performático o bastante para essa quantidade de dados.

# 3. TESTE DE BANCO DE DADOS E ANÁLISE

## 3.2.1 Trade-Off
Para os DDL decidi fazer uma modelagem HÍBRIDA
Tabelas normalizadas para operados e despesas
despesas_agregadas DESNORMALIZADAS

Motivos: Normalizadas mantém a integridade de dados
         Desnormalizadas Performace em queries analíticas
## 3.2.2 Trade-Off
Tipos de dados -> Valores monetários = NUMERIC(15,2) MOTIVO = Precisão
DATAS = INTEGER MOTIVO = Comodidade, dados ja vem assim
