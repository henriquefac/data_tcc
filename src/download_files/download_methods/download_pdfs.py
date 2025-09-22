from configPy import DirManager
import requests
import os


URL_BASE = os.getenv("URL_BASE")
FONTE_DOCS = os.getenv("FONTE_DOCS")
COMPLEMENTO = "?doc="

def get_url(file:str):
    return f"{URL_BASE}{FONTE_DOCS}{COMPLEMENTO}{file}"


def download_single_file_pdf(file:str,file_name:str,output_dir:DirManager):
    url = get_url(file)
    path_file = output_dir.create_file_path(file_name, "pdf")
    
    try:
        resp = requests.get(url)
        resp.raise_for_status()

        with open(path_file, "wb") as pdf_file:
            pdf_file.write(resp.content)
        return f"{file_name} baixado com sucesso em {output_dir.dir_path}"
    except Exception as e:
        return f"Falha ao baixar {file_name}: {e}"

