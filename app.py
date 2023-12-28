import csv
from datetime import datetime
import json
import os
import time
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Requisicao, Resumo

engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def load_payload(payload_format):
    '''Carrega os dados de payload a partir de um arquivo CSV ou entrada JSON.

    Parâmetros:
    - payload_format (str): Formato do payload ('CSV' ou 'JSON')

    Retorna:
    - list: Lista de dicionários contendo os payloads
    '''
    data = []

    if payload_format.lower() == 'csv':
        csv_filename = 'data.csv'
        if os.path.exists(csv_filename):
            try:
                with open(csv_filename, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        data.append(row)
                    return data
            except FileNotFoundError:
                print(f'Arquivo CSV {csv_filename} não encontrado.')
                return None
        else:
            print('É necessário fornecer o nome do arquivo CSV.')
            return None
    elif payload_format.lower() == 'json':
        user_input = input('Insira o payload no formato JSON: ')
        try:
            json_data = json.loads(user_input)
            data.append(json_data)
            return data
        except json.JSONDecodeError:
            print('O payload inserido não é um JSON válido.')
            return None
    else:
        print('Formato de payload não suportado.')
        return None


def from_data_request(url, method, num_requests, timeout, data_inicio):
    '''
    Realiza as requisições do tipo POST, PUT ou PATCH com payload.

    Parâmetros:
    - url (str): URL para requisição
    - method (str): Método HTTP (POST, PUT ou PATCH)
    - num_requests (int): Número de requisições a serem feitas
    - timeout (int): Tempo limite por requisição
    - data_inicio (datetime): Data e hora de início dos testes

    Retorna:
    None
    '''
    total_time = 0
    max_time = float('-inf')
    requests_done = 0
    successes = 0
    failures = 0
    headers = {'Content-Type': 'application/json'}
    requisicoes = []

    payload_format = input('Payload Format: (CSV,JSON) ')
    payloads = load_payload(payload_format)
    if payloads:
        while requests_done < num_requests:
            for payload in payloads:
                start_time = time.time()
                try:
                    if method == 'POST':
                        response = requests.post(
                            url, data=json.dumps(payload), headers=headers, timeout=timeout)
                    elif method == 'PATCH':
                        response = requests.patch(
                            url, data=json.dumps(payload), headers=headers, timeout=timeout)
                    elif method == 'PUT':
                        response = requests.put(
                            url, data=json.dumps(payload), headers=headers, timeout=timeout)
                    if response.status_code == 200:
                        successes += 1
                        result = 'Sucesso'
                    else:
                        failures += 1
                        result = 'Falha'

                except Exception as ex:
                    failures += 1
                    result = 'Falha'

                requests_done += 1
                elapsed_time = time.time() - start_time
                total_time += elapsed_time
                max_time = max(max_time, elapsed_time)
                payload_str = json.dumps(payload)
                response_str = str(response)

                requisicao = Requisicao(
                    url=url, payload=payload_str, formato=method, tempo_limite=timeout, status_code=response.status_code, response=response_str, resultado=result, tempo=elapsed_time)
                requisicoes.append(requisicao)

                print(f'Resultado: {result} | Tempo gasto: {
                    elapsed_time:.2f} segundos')
                print('Resposta:')
                print(f'{response.text}')
                print('-' * 50)

                session.add(requisicao)
    else:
        print('Nenhum dado encontrado para realizar as solicitações')

    save_report_and_print(requisicoes, num_requests,
                          successes, failures, max_time, total_time, data_inicio)


def from_query_request(url, method, num_requests, timeout, data_inicio):
    '''
    Realiza as requisições do tipo GET ou DELETE sem payload.

    Parâmetros:
    - url (str): URL para requisição 
    - method (str): Método HTTP (GET ou DELETE)
    - num_requests (int): Número de requisições a serem feitas
    - timeout (int): Tempo limite por requisição
    - data_inicio (datetime): Data e hora de início dos testes

    Retorna:
    None
    '''
    total_time = 0
    max_time = float('-inf')
    successes = 0
    failures = 0
    requisicoes = []
    for _ in range(num_requests):
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(url, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=timeout)
            if response.status_code == 200:
                successes += 1
                result = 'Sucesso'
            else:
                failures += 1
                result = 'Falha'
        except Exception as ex:
            failures += 1
            result = 'Falha'
        elapsed_time = time.time() - start_time
        total_time += elapsed_time
        max_time = max(max_time, elapsed_time)
        response_str = str(response)

        requisicao = Requisicao(
            url=url, payload='', formato=method, tempo_limite=timeout, status_code=response.status_code, response=response_str, resultado=result, tempo=elapsed_time)
        requisicoes.append(requisicao)

        print(f'Resultado: {result} | Tempo gasto: {
            elapsed_time:.2f} segundos')
        print('Resposta:')
        print(f'{response.text}')
        print('-' * 50)

    save_report_and_print(requisicoes, num_requests, successes,
                          failures, max_time, total_time, data_inicio)


def get_num_requests():
    '''
    Obtém o número de requisições que o usuário deseja fazer.

    Retorna:
    - int: Número de requisições
    '''
    num_requests = input('Numero de requests: ')
    try:
        num_requests = int(num_requests)
        return num_requests
    except Exception as ex:
        print(f'Erro ao tentar converser a entrada {
            num_requests} para INT', ex)


def get_timeout():
    '''
    Obtém o tempo limite por requisição definido pelo usuário.

    Retorna: 
    - int: Tempo limite em segundos
    '''
    timeout = input('Insira o tempo limite por chamada: ')
    try:
        timeout = int(timeout)
        return timeout
    except Exception as ex:
        print(f'Erro ao tentar converser a entrada {
            timeout} para INT', ex)


def save_report_and_print(requisicoes, num_requests, successes, failures, max_time, total_time, data_inicio):
    '''
    Salva o relatório em um arquivo .txt e no banco de dados.
    Imprime o resumo dos testes.

    Parâmetros:
    - requisicoes (list): Lista de objetos Requisicao
    - num_requests (int): Número total de requisições
    - successes (int): Número de requisições bem-sucedidas
    - failures (int): Número de falhas nas requisições
    - max_time (float): Tempo máximo de requisição
    - total_time (float): Tempo total de requisições
    - data_inicio (datetime): Data e hora de início dos testes

    Retorna:
    None
    '''
    avg_time = total_time / num_requests if num_requests > 0 else 0
    data_termino = datetime.now()
    print('\nResumo do Teste:')
    print(f'Número total de requisições: {num_requests}')
    print(f'Número de sucessos: {successes}')
    print(f'Número de falhas: {failures}')
    print(f'Tempo médio por requisição: {avg_time:.2f} segundos')
    print(f'Tempo máximo de requisição: {max_time:.2f} segundos')

    resumo = Resumo(data_inicio=data_inicio,
                    data_termino=data_termino,
                    total=num_requests,
                    sucessos=successes,
                    falhas=failures,
                    tempo_medio=avg_time,
                    tempo_maximo=max_time)
    session.add(resumo)
    session.commit()
    print(f"Resumo ID: {resumo.id}")
    for requisicao in requisicoes:
        requisicao.id_resumo = resumo.id

    filename = f'relatorio_final.txt'
    with open(filename, 'w') as file:
        for requisicao in requisicoes:
            file.write('Resultado: ' + str(requisicao.resultado) +
                       ' | Tempo gasto: ' + str(requisicao.tempo) + '\n')
            file.write('Resposta:\n' + str(requisicao.response) + '\n')
            file.write('-' * 50 + '\n')

        file.write('\nResumo do Teste:\n')
        file.write(f'Número total de requisições: {num_requests}\n')
        file.write(f'Número de sucessos: {successes}\n')
        file.write(f'Número de falhas: {failures}\n')
        file.write(f'Tempo médio por requisição: {avg_time:.2f} segundos\n')
        file.write(f'Tempo máximo de requisição: {max_time:.2f} segundos\n')

    session.add_all(requisicoes)
    session.commit()
    session.close()
    print(f'O relatório foi salvo no arquivo: {
          filename} e também no banco de dados')
    print('Agradecemos sua participação')


def main():
    '''
    Função principal que executa o programa.

    Lê as entradas do usuário e chama as funções para executar as requisições.
    
    Retorna:
    None
    '''
    print('Caso sua rota seja GET, insira por favor, a url completa com parametros e valores')
    print('Caso sua rota seja POST e etc., insira apenas a url, em seguida será requisitado csv ou json com os dados')
    url = input('Insira a url da rota que deseja testar: ')
    method = input('Insira que tipo de request você fara a rota: ')
    method = method.upper()

    num_requests = get_num_requests()
    timeout = get_timeout()
    data_inicio = datetime.now()
    if method == 'POST' or method == 'PATCH' or method == 'PUT':
        from_data_request(url, method, num_requests, timeout, data_inicio)
    elif method == 'GET' or method == 'DELETE':
        from_query_request(url, method, num_requests, timeout, data_inicio)
    else:
        print('Método não suportado')
    session.commit()
    session.close()


if __name__ == '__main__':
    main()
