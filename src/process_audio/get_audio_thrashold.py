from configPy import Config, DirManager
from pathlib import Path
import numpy as np
import subprocess
import csv
from tqdm import tqdm

files_dir = Config.get_dir_files()
audio_dir = files_dir["audios"]

# arquivo CSV de saída
out_path_file = files_dir.create_file_path("thresholds", "csv")

sample_rate = 16000
channels = 1
bytes_per_sample = 2
block_size_sec = 0.1
block_size_bytes = int(block_size_sec * sample_rate * channels * bytes_per_sample)

cmd = lambda x: [
    "ffmpeg", "-i", str(x),
    "-f", "s16le", "-acodec", "pcm_s16le",
    "-ac", str(channels), "-ar", str(sample_rate), "-"
]

proc_lambda = lambda x: subprocess.Popen(
    cmd(x), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
)

eps = 1e-10

def get_stream_threshold(path: Path):
    proc = proc_lambda(path)
    energies_db = []

    while True:
        raw = proc.stdout.read(block_size_bytes)
        if not raw:
            break

        samples = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
        if samples.size == 0:
            continue
        rms = np.sqrt(np.mean(samples**2))
        energies_db.append(20 * np.log10(max(rms, eps)))

    if len(energies_db) == 0:
        return None, None

    energies_db = np.array(energies_db)

    silence_threshold = np.percentile(energies_db, 5)
    murmur_threshold = np.percentile(energies_db, 15)

    return silence_threshold, murmur_threshold


def process_file(path: Path, sobreescrever:bool = False):
    if not out_path_file.exists():
        with open(out_path_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["filename", "silence_threshold_db", "murmur_threshold_db"])

    try:
        data = np.genfromtxt(out_path_file, delimiter=",", dtype=str, skip_header=1)
        if data.ndim == 1 and data.size == 0:
            filenames = []
        elif data.ndim == 1:
            filenames = [data[0]]
        else:
            filenames = data[:, 0].tolist()
    except Exception:
        filenames = []

    filename = path.stem

    # Verifica se já existe e não deve sobrescrever
    if filename in filenames and not sobreescrever:
        raise Exception(f"Já foi calculado o Threshold desse arquivo: {path}")
    # Calcula thresholds    
    st, mt = get_stream_threshold(path)

    with open(out_path_file, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([filename, st, mt])



def process_all_and_save():
    files = list(audio_dir.list_files().values())

    with open(out_path_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Cabeçalho
        writer.writerow(["filename", "silence_threshold_db", "murmur_threshold_db"])

        for f in tqdm(files, desc="Calculando thrasholds"):
            silence, murmur = get_stream_threshold(f)
            if silence is None:
                continue
            writer.writerow([f.stem, silence, murmur])


__all__ = ["process_file", "process_all_and_save", "get_stream_threshold"]
