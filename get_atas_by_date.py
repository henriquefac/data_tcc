from configPy import Config, DirManager
from pathlib import Path
import json
import shutil

file_dir = Config.get_dir_files()
atas_dir = file_dir["atas"]
audios_dir= file_dir["audios"]
# samples

sample_dir = file_dir.create_dir("samples")

# separar entre audios e atas
atas_sample_dir = sample_dir.create_dir("atas")
audios_sample_dir = sample_dir.create_dir("audios")

# pegar todas as atas
def get_all_files(dir_path:DirManager):
    return list(dir_path.list_files().values())


atas_f_path = get_all_files(atas_dir)
audios_f_path = get_all_files(audios_dir)

# para cada lista em cada ano, organizar do mais valho para o mais novo
def set_value_for_date(path_str: str) -> int:
    name_file = path_str.split("/")[-1]
    parts = name_file.split("-")

    try:
        day = int(parts[2])
        month = int(parts[3])
    except (IndexError, ValueError):
        print("Erro ao extrair data de:", path_str)
        return 0

    # lineariza como MMDD → ex: 502 (5 de fevereiro)
    return month * 100 + day

def sample_equally(paths: list[str], n: int = 5):
    total = len(paths)
    if total <= n:
        return paths  # se não tem elementos suficientes, retorna todos

    step = total / n
    indices = [int(i * step) for i in range(n)]
    return [paths[i] for i in indices]

def get_dict(sampled: bool = False):
    dict_date = {}
    for f in atas_f_path:
        parts = str(f).split("-")
        if len(parts) >= 5:
            year = parts[4]
            dict_date.setdefault(year, []).append(str(f))
        else:
            print("Nome inesperado:", f)

    # ordenar cada lista
    for year, paths in dict_date.items():
        paths = sorted(paths, key=set_value_for_date)
        if sampled:
            dict_date[year] = sample_equally(paths, 5)
        else:
            dict_date[year] = paths

    return dict_date

# a partir do dicionário de atas, procurar a contraparte de áudio
def get_audio_dict(dict_atas:dict):
    dict_output = {}
    for key in dict_atas:
        list_files = dict_atas[key]
        dict_output[key] = list(map(lambda x: audios_dir[f"{Path(x).stem}.webm"], list_files))
    return dict_output

if __name__ == "__main__":
    dict_atas_samples = get_dict(True)
    dict_audios_samples = get_audio_dict(dict_atas_samples)

    list_atas_dir = []
    list_audios_dir = []

    for key in dict_atas_samples:
        list_atas_dir.append(atas_sample_dir.create_dir(key))
        list_audios_dir.append(audios_sample_dir.create_dir(key))

        for f in dict_atas_samples[key]:
            shutil.copy(f, str(list_atas_dir[-1].dir_path))
        
        for f in dict_audios_samples[key]:
            shutil.copy(f, str(list_audios_dir[-1].dir_path))

    
