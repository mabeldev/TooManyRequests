import csv
import json
import os
import time
import requests


def load_payload(payload_format):
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


def from_data_request(url, method, num_requests, timeout):
    responses = []
    total_time = 0
    max_time = float('-inf')
    requests_done = 0
    successes = 0
    failures = 0
    headers = {'Content-Type': 'application/json'}

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

                responses.append({
                    'Resultado': result,
                    'Tempo gasto': f'{elapsed_time:.2f} segundos',
                    'Resposta': f'{response.text}'
                })

                print(f'Resultado: {result} | Tempo gasto: {
                    elapsed_time:.2f} segundos')
                print('Resposta:')
                print(f'{response.text}')
                print('-' * 50)
    else:
        print('Nenhum dado encontrado para realizar as solicitações')

    avg_time = total_time / num_requests if num_requests > 0 else 0
    print('\nResumo do Teste:')
    print(f'Número total de requisições: {num_requests}')
    print(f'Número de sucessos: {successes}')
    print(f'Número de falhas: {failures}')
    print(f'Tempo médio por requisição: {avg_time:.2f} segundos')
    print(f'Tempo máximo de requisição: {max_time:.2f} segundos')


def from_query_request(url, method, num_requests, timeout):
    responses = []
    total_time = 0
    max_time = float('-inf')
    successes = 0
    failures = 0

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
        
        responses.append({
            'Resultado': result,
            'Tempo gasto': f'{elapsed_time:.2f} segundos',
            'Resposta': f'{response.text}'
        })

        print(f'Resultado: {result} | Tempo gasto: {
            elapsed_time:.2f} segundos')
        print('Resposta:')
        print(f'{response.text}')
        print('-' * 50)

    avg_time = total_time / num_requests if num_requests > 0 else 0
    print('\nResumo do Teste:')
    print(f'Número total de requisições: {num_requests}')
    print(f'Número de sucessos: {successes}')
    print(f'Número de falhas: {failures}')
    print(f'Tempo médio por requisição: {avg_time:.2f} segundos')
    print(f'Tempo máximo de requisição: {max_time:.2f} segundos')


def get_num_requests():
    num_requests = input('Numero de requests: ')
    try:
        num_requests = int(num_requests)
        return num_requests
    except Exception as ex:
        print(f'Erro ao tentar converser a entrada {
            num_requests} para INT', ex)


def get_timeout():
    timeout = input('Insira o tempo limite por chamada: ')
    try:
        timeout = int(timeout)
        return timeout
    except Exception as ex:
        print(f'Erro ao tentar converser a entrada {
            timeout} para INT', ex)


def main():
    url = input('Insira a url da rota que deseja testar: ')
    method = input('Insira que tipo de request você fara a rota: ')
    method = method.upper()

    num_requests = get_num_requests()
    timeout = get_timeout()

    if method == 'POST' or method == 'PATCH' or method == 'PUT':
        from_data_request(url, method, num_requests, timeout)
    elif method == 'GET' or method == 'DELETE':
        from_query_request(url, method, num_requests, timeout)
    else:
        print('Método não suportado')


if __name__ == '__main__':
    main()
