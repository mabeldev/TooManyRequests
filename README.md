# Projeto destinado a realizar testes de multiplas requests a rota definida pelo usuário
## Tecnologias e Frameworks
- Python
- SQLAlchemy
- SQLite
## Fluxo da aplicação
1. Clone este repositório:
git clone https://github.com/mabeldev/TooManyRequests.git



2. Acesse a pasta do projeto:
cd TooManyRequests



3. Crie um ambiente virtual:
python -m venv venv 



4. Ative o ambiente virtual:
#### Windows
venv\Scripts\activate

#### Linux/Mac
source venv/bin/activate



5. Instale as dependências:
pip install -r requirements.txt



6. Execute a aplicação:
python app.py



Siga as instruções exibidas no terminal para informar a URL e o método HTTP a ser testado.

Ao final, será gerado um relatório com o resumo dos testes.

## Métodos principais
### main()
Método principal que inicia o fluxo da aplicação.

Solicita ao usuário a URL da rota a ser testada e o método HTTP (GET, POST, etc).

Chama os métodos específicos de acordo com o método HTTP informado.

### make_request()
Utilizado para métodos HTTP que enviam uma carga (body) na requisição ou via paramêtro na url.

Lê os payloads a serem enviados de um arquivo CSV ou JSON.

Realiza as requisições em loop com os payloads.

Salva cada requisição realizada no banco de dados.

Gera o relatório final com o resumo.


### save_report()
Recebe os dados coletados durante os testes.

Salva o resumo geral no banco de dados.

Imprime o resumo no console.

Gera um arquivo texto com os detalhes de todas as requisições.

Dessa forma, o app.py provê uma maneira simples de testar requisições HTTP contra uma API e analisar o desempenho e resultados.

### save_txt_report()
Recebe os dados coletados durante os testes.

Exporta o resumo geral na raiz do projeto no arquivo relatorio_final.txt