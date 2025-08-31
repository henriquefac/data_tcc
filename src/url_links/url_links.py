from configPy import Config, DirManager
from pathlib import Path
import csv
import requests
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

import json

load_dotenv()

# URL base e endpoint
URL_BASE = os.getenv("URL_BASE")
FONTE_SESSOES = os.getenv("FONTE_SESSOES")



data_range = [(2020, 3), (2025, 8)]

files_dir = Config.get_dir_files()
sessoes_dir = files_dir.create_dir("sessoes_url")

def get_sessions(anomes):
    # Monta a URL final
    url = f"{URL_BASE}{FONTE_SESSOES}?anomes={anomes}"
    
    # Faz a requisição GET
    resposta = requests.get(url)
    resposta.raise_for_status()  # Gera erro se status != 200
    
    # Converte para JSON
    dados = resposta.json()
    return dados


# pegar datas das sessoes de interesse

def data_sessoes():
    mes = data_range[0][1]
    for i in range(data_range[1][0] - data_range[0][0]):
        ano = data_range[0][0] + i
        while mes > 0:
            yield f"{ano}{mes:02d}"
            mes = (mes + 1)%13
        mes = 1
    for i in range(mes, data_range[1][1]+1):
        yield f"{data_range[1][0]}{i:02d}"


# tenho que criar a pasta que vai conter os arquivos de csv
# cada um relativo a um mês, one cada linha é uma sessao que ocorreu
# primeira coluna representa a url da ATA e 

def get_dir_for_files(file_name)-> Path:
    return sessoes_dir.create_file_path(file_name, "csv")

# com os caminhos criados, tenho que escrever em cada um
# uma linha para cada sessao, duas colunbas
# URL da ata e link do vídeo no youtube
def right_csv_file(file_name: str, data: list[list[str]])->None:
    # CRIAR ARQUIVO PARA ESCREVER
    file_path = sessoes_dir.create_file_path(file_name, 'csv')

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(data)
# Do json, pegar url da ATA e link do youtube

def aux_get_data_json(json_data: dict):
    url_ata = [a["url"] for a in json_data.get("atas", [])]
    link_video = [a["link"] for a in json_data.get("videos", [])]
    if not url_ata or not link_video:
        return None
    return [url_ata[0], link_video[0]]

def get_data_from_json(json_data_list: dict):
    list_data = [tupla for tupla in list(map(aux_get_data_json, json_data_list["dados"])) if tupla ]
    return list_data

def fetch_and_parse(month: str):
    return get_data_from_json(get_sessions(month))


# FUNCAO PRINCIPAL PARA ADIQUIRIR OS DADOS
def get_data_main(get_data: bool = False):
    if sessoes_dir.has_files() and not get_data:
        return sessoes_dir
    # MES QUE OCORRRAM AS SESSOES
    session_month = list(data_sessoes()) # lista de strings com todas as sessões
    
    # PARA CADA, PEGAR URL DA ATA E GRAVAÇÃO DA SESSÃO
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_month = {executor.submit(fetch_and_parse, m): m for m in session_month}

        for future in as_completed(future_to_month):
            month = future_to_month[future]

            try:
                data = future.result()
                results.append((month, data))
                print(f"Pacote Json das sessoes do mês {month[4:]} do ano {month[:4]} foi recuperado")
            except Exception as e:
                print(f"Erro ao capturar pacote Json das sessoes do mês {month[4:]} do ano {month[:4]}: {e}")

    # escrever arquivos
    for month, data in results:
        if data:
            right_csv_file(month, data)

    return sessoes_dir
if __name__ == "__main__":
    get_data_main()
