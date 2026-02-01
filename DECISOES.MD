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
Dados sem CNPJ Apenas RegistoANS; entretanto mais adiante no case
é necessário fazer um JOIN E pegar CNPJ, LOGO, vou criar a COLLUM e incias com 
valor DEFAULT=PENDENTE para que em seguida possa fazer um JOIN.

Sobre as inconsistencias como valores negativos e zerados vou manter,
entretanto, vou somar eles para ter essa informação.

# 2. TESTE DE TRANSFORMAÇÃO E VALIDAÇÃO DE DADOS
Tinha feito um validador na classe DataProcessor,
entretanto como vou verificar os CNPJs decidi modularizar 
e criar uma classe específica para isso, pois caso
mude a lógica de négocio seja fácil de refatorar.
### Trade-Off
Decidi armazenar todo os dados, entretanto, pegar
as estastisticas dessas inconsistencias e armazenar
os CNPJs duplicados.
