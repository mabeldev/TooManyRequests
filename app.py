import csv
from datetime import datetime
import json
import os
import time
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Requisicao, Resumo


class App:
    def __init__(self):
        self.engine = create_engine('sqlite:///database.db')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def load_payload(self, payload_format):
        '''Carrega os dados de payload a partir de um arquivo CSV ou entrada    JSON.

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

    def make_request(self, url, method, num_requests, timeout, start_time):
        '''
        Realiza requisições HTTP para a URL informada utilizando o método especificado
        e captura métricas sobre as requisições.

        Parâmetros:
        - url (str): A URL para realizar as requisições
        - method (str): O método HTTP a ser utilizado (GET, POST, etc)
        - num_requests (int): O número de requisições a serem feitas
        - timeout (int): O tempo limite em segundos para cada requisição
        - start_time (datetime): A hora de início das requisições

        Retorna:
        - None
        '''
        total_time = 0
        max_time = float('-inf')
        successes = 0
        failures = 0
        list_requests = []
        method = method.upper()

        if method in ('POST', 'PUT', 'PATCH'):
            payload_format = input(
                'Insira o formato do payload: (CSV ou JSON) ')
            payload_data = self.load_payload(payload_format)
            for payload in payload_data:
                for i in range(num_requests):
                    start = time.time()
                    try:
                        if method == 'POST':
                            response = requests.post(
                                url, json=payload, timeout=timeout)
                        elif method == 'PUT':
                            response = requests.put(
                                url, json=payload, timeout=timeout)
                        elif method == 'PATCH':
                            response = requests.patch(
                                url, json=payload, timeout=timeout)
                        if response.ok:
                            result = 'Sucesso'
                            successes += 1
                        else:
                            result = 'Falha'
                            failures += 1
                    except:
                        result = 'Falha'
                        failures += 1

                    payload_str = json.dumps(payload)
                    response_str = str(response)
                    end = time.time()
                    elapsed = end - start
                    total_time += elapsed
                    max_time = max(max_time, elapsed)

                    request = Requisicao(
                        url=url,
                        payload=payload_str,
                        formato=method,
                        tempo_limite=timeout,
                        status_code=response.status_code,
                        response=response_str,
                        resultado=result,
                        tempo=elapsed)

                    list_requests.append(request)
        elif method in ('GET', 'DELETE'):
            for i in range(num_requests):
                start = time.time()
                try:
                    if method == 'GET':
                        response = requests.get(url, timeout=timeout)
                    elif method == 'DELETE':
                        response = requests.delete(url, timeout=timeout)
                    if response.ok:
                        result = 'Sucesso'
                        successes += 1
                    else:
                        result = 'Falha'
                        failures += 1
                except:
                    result = 'Falha'
                    failures += 1

                response_str = str(response)
                end = time.time()
                elapsed = end - start
                total_time += elapsed
                max_time = max(max_time, elapsed)

                request = Requisicao(
                    url=url,
                    payload='',
                    formato=method,
                    tempo_limite=timeout,
                    status_code=response.status_code,
                    response=response_str,
                    resultado=result,
                    tempo=elapsed)
                list_requests.append(request)
        else:
            print("Método não suportado")
        self.save_report(list_requests, num_requests,
                         successes, failures, max_time, total_time, start_time)

    def get_num_requests(self):
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
            print(f'Erro ao tentar converser a entrada 
                  {num_requests} para INT', ex)

    def get_timeout(self):
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

    def save_report(self, requisicoes, num_requests, successes, failures, max_time, total_time, start_time):
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
        session = sessionmaker(bind=self.engine)()

        avg_time = total_time / num_requests if num_requests > 0 else 0
        data_termino = datetime.now()
        print('\nResumo do Teste:')
        print(f'Número total de requisições: {num_requests}')
        print(f'Número de sucessos: {successes}')
        print(f'Número de falhas: {failures}')
        print(f'Tempo médio por requisição: {avg_time:.2f} segundos')
        print(f'Tempo máximo de requisição: {max_time:.2f} segundos')

        resumo = Resumo(data_inicio=start_time,
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

        self.save_txt_report(requisicoes, num_requests,
                             successes, failures, max_time, avg_time)

        session.add_all(requisicoes)
        session.commit()
        session.close()
        print('Relatório salvo no banco de dados com sucesso!')

    def save_txt_report(self, requisicoes, num_requests, successes, failures, max_time, avg_time):
        '''
        Salva o relatório de testes em um arquivo texto.

        Parâmetros:
        - requisicoes (list): Lista de objetos Requisicao
        - num_requests (int): Número total de requisições 
        - successes (int): Número de requisições bem-sucedidas
        - failures (int): Número de falhas nas requisições
        - max_time (float): Tempo máximo de requisição
        - avg_time (float): Tempo médio de requisição
        
        Retorna:
        - None
        '''
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
            file.write(f'Tempo médio por requisição: {
                       avg_time:.2f}     segundos\n')
            file.write(f'Tempo máximo de requisição: {
                       max_time:.2f}     segundos\n')
        print(f'O relatório foi salvo no arquivo: {filename}')

    def run(self):
        print('Informe URL do tipo GET com parâmetros ou apenas endpoint para   outros métodos')
        url = input('Informe a URL: ')
        method = input('Informe o método (GET, POST, etc): ')

        num_requests = self.get_num_requests()
        timeout = self.get_timeout()
        start_time = datetime.now()

        self.make_request(
            url, method, num_requests, timeout,  start_time)


if __name__ == '__main__':
    app = App()
    app.run()
