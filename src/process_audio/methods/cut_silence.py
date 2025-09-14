import subprocess
from configPy import Config, DirManager
from pathlib import Path
import numpy as np

file_dir = Config.get_dir_files()
csv_file = file_dir["thresholds.csv"]

def read_csv_as_dir() -> dict[str, float]:
    """
    Lê o CSV de thresholds e retorna um dicionário:
    {nome_arquivo: threshold_silencio}
    """
    try:
        data = np.genfromtxt(fname=str(csv_file), delimiter=",", dtype=str, skip_header=1)
        thresholds = {}

        if data.ndim == 1:  # Apenas 1 linha no CSV
            filename, silence, murmur = data
            thresholds[filename] = max(float(murmur), -50)
        else:
            for row in data:
                filename, silence, murmur = row
                thresholds[filename] = max(float(murmur), -50)

        return thresholds

    except Exception as e:
        print(f"Erro ao ler CSV {csv_file}: {e}")
        return {}


def remove_silence(input_path: Path, output_path: DirManager,
                   threshold_db: float = None, min_silence_len:float = 1.2,
                   remove_leading_trailing: bool = True, debug: bool = False):
    name_file = input_path.stem
    suffix = "wav"
    wav_file_cut = output_path.create_file_path(name_file + "_cut", suffix=suffix)

    # Caso não tenha threshold definido, tenta buscar no CSV
    if threshold_db is None:
        thresholds = read_csv_as_dir()
        if name_file in thresholds:
            threshold_db = thresholds[name_file]

            print("Em decibeis: ",threshold_db)
        else:
            raise ValueError(f"Nenhum threshold encontrado para {name_file} no CSV")

    # Define parâmetros para ffmpeg
    params = f"stop_periods=-1:stop_threshold={threshold_db}dB:stop_duration={min_silence_len}"
    if remove_leading_trailing:
        params = (
            f"start_periods=1:start_threshold={threshold_db}dB:start_duration={min_silence_len}:"
            + params
        )

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-af", f"silenceremove={params}",
        str(wav_file_cut)
    ]

    subprocess.run(
        cmd,
        stdout=None if debug else subprocess.DEVNULL,
        stderr=None if debug else subprocess.DEVNULL,
        check=True
    )

    return wav_file_cut       
