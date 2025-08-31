from configPy import Config, DirManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
from tqdm import tqdm
from pathlib import Path

files_dir = Config.get_dir_files()
audios_dir = files_dir["audios"]

# diretório dos audios convertidos para WAV
audios_wav_dir = files_dir.create_dir("audios_wav")

def get_files():
    return [f[1] for f in audios_dir.list_files().items()]

def convert_audio(input_audio: Path, output_dir: DirManager, ar:int = 44100, ac:int = 1, show_log:bool = False):
    try:
        output_audio = output_dir.create_file_path(input_audio.stem, "wav", exist_ok=True)
    except:
        return "Já existe"

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "quiet" if not show_log else "info",
        "-i", str(input_audio),
        "-ar", str(ar),
        "-ac", str(ac),
        "-c:a", "pcm_s16le",
        str(output_audio)
    ]

    try:
        subprocess.run(cmd, check=True)
        return output_audio
    except subprocess.CalledProcessError as e:
        return f"Falhou: {input_audio} (exit {e.returncode})"

def convert_all_audio(max_workers: int = 5):
    all_files = get_files()
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert_audio, f, audios_wav_dir): f for f in all_files}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Convertendo audios"):
            audio_path = future.result()
            results.append(audio_path)


    return results
