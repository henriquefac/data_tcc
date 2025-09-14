from configPy import Config, DirManager
from pathlib import Path
import numpy as np
import requests
import os


URL_BASE = os.getenv("URL_BASE")
FONTE_DOCS = os.getenv("FONTE_DOCS")
COMPLEMENTO = "?doc="


files_dir = Config.get_dir_files()

sessoes_dir = files_dir["sessoes_url"]

atas_path = files_dir.create_dir("atas") # diretório das atas de reunião




# listar arquivos csv com url's das atas das sessoes

def get_files():
    return [f[1] for f in sessoes_dir.list_files().items()]


# de cada arquivo estrair primeira coluna
def get_url_from_file(path_file: Path):
    try:
        # Lê todas as linhas, pega apenas a primeira coluna
        data = np.loadtxt(path_file, delimiter=",", dtype=str, encoding="utf-8", ndmin=2)
        return data[:, 0].tolist()
    except Exception as e:
        print(f"Erro ao processar {path_file}: {e}")
        return []
# cada string (url) é um pdf para ser baixado

def download_all_pdfs(exists:bool = True):
    files = get_files()
    for f in files:
        urls = get_url_from_file(f)
        for url_parcial in urls:
            url_final = f"{URL_BASE}{FONTE_DOCS}{COMPLEMENTO}{url_parcial}"
            nome_arquivo = ("-".join(url_parcial.split("|")[2:]))[:-4]
            destino = atas_path.create_file_path(nome_arquivo, "pdf")


            if destino.exists() and exists:
                print(f"{nome_arquivo} já existe, pulando...")
                continue

            try:
                resp = requests.get(url_final)
                resp.raise_for_status()
                with open(destino, "wb") as pdf_file:
                    pdf_file.write(resp.content)
                print(f"{nome_arquivo} baixado com sucesso.")
            except Exception as e:
                print(f"Erro ao baixar {url_final}: {e}")

