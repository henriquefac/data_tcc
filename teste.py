from configPy import Config, DirManager
from pytubefix import YouTube
from pathlib import Path
import numpy as np

files_dir = Config.get_dir_files()
sessoes_dir = files_dir["sessoes_url"]


# Função para recuperar os paths dos arquivos
def get_files():
    return [f[1] for f in sessoes_dir.list_files().items()]

def get_link_videos(path: Path):
    try:
        data = np.loadtxt(path, dtype=str, delimiter=',', encoding='utf-8', ndmin=2)
        # transformar url em apenas os nomes de cada sessao
        vec_func = np.vectorize(lambda x: x.split("|")[-1])
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



all_links = collect_all_links()

sample = all_links[0][1]

yt = YouTube(sample)
stream = yt.streams.filter(only_audio=True)

print(type(stream))
