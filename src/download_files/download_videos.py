from configPy import Config, DirManager
from pathlib import Path
from pytubefix.query import StreamQuery 
from pytubefix import YouTube
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import numpy as np
from tqdm import tqdm
# diretorio de arquivos
files_dir = Config.get_dir_files()

sessoes_dir = files_dir["sessoes_url"]

video_dir = files_dir.create_dir("audios")


# valores de itag

ITAGS = ["251", "140", "139"]

# dicionario para mapear os tipos de arquivos para sua extenção correta

EXT_MAP = {
    "audio/webm": "webm",
    "audio/mp4": "m4a"
}

# Função para recuperar os paths dos arquivos
def get_files():
    return [f[1] for f in sessoes_dir.list_files().items()]

def get_link_videos(path: Path):
    try:
        data = np.loadtxt(path, dtype=str, delimiter=',', encoding='utf-8', ndmin=2)
        # transformar url em apenas os nomes de cada sessao
        vec_func = np.vectorize(lambda x: ("-".join(x.split("|")[2:]))[:-4])
        data[:, 0] = vec_func(data[:, 0])
        return data
    except Exception as e:
        print(f"Erro {e} ao tentar buscar os links do seguibnte arquivo: {path}")
        return np.array([])

def collect_all_links():
    all_data = []
    for f in get_files():
        data = get_link_videos(f)
        if data.size > 0:
            all_data.extend(data.tolist())
    return all_data

def select_stream(streamQuerry:StreamQuery):
    for itag in ITAGS:
        s = streamQuerry.get_by_itag(itag=itag)
        if s:
            return s

    return streamQuerry.order_by("abr").desc().first()


def download_single_audio(name_session: str, link_video: str, download_if_exists:bool = False):
    try:
        link_video = link_video.strip()
        yt = YouTube(link_video)
        stream = select_stream(yt.streams.filter(only_audio=True))
        if not stream:
            raise RuntimeError("Nenhum stream disponível")
        
        # identificar sufixo
        ext = EXT_MAP.get(stream.mime_type, ".m4a")

        filename = f"{name_session}.{ext}"
        output_dir_path = video_dir.dir_path
        
        if (output_dir_path / filename).exists() and download_if_exists:
            return f"Áudio já existe"

        output = stream.download(output_path=output_dir_path, filename=filename)
        return f"Áudio baixado do vídeo {link_video} em {output}"
    except Exception as e:
        return f"Erro ao baixar áudio do video {link_video}: {e}"


# fazer download de todos os vídeos

def download_all_audios(max_workers: int = 5, donwload_if_exists: bool = False):
    all_links = collect_all_links()
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_single_audio, name, link, donwload_if_exists) : {name, link} for name, link in all_links}
        for future in tqdm(as_completed(futures), total = len(futures), desc="Baixando vídeos"):
            results.append(future.result())
            
