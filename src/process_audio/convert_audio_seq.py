from configPy import Config, DirManager
import subprocess
from pathlib import Path
from tqdm import tqdm

files_dir = Config.get_dir_files()
audios_dir = files_dir["audios"]

# diretório dos audios convertidos para WAV
audios_wav_dir = files_dir.create_dir("audios_wav")

def get_files():
    """Gera arquivos um a um, evitando criar lista completa em memória"""
    for _, f in audios_dir.list_files().items():
        yield f

def convert_audio(input_audio: Path, output_dir: DirManager, ar:int = 44100, ac:int = 1, show_log:bool = False):
    """Converte um único arquivo para WAV PCM"""
    try:
        output_audio = output_dir.create_file_path(input_audio.stem, "wav", exist_ok=True)
    except:
        return f"Já existe: {input_audio}"

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "quiet" if not show_log else "info",
        "-y",
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

def convert_all_audio_seq():
    """Converte todos os áudios sequencialmente"""
    results = []
    for f in tqdm(get_files(), desc="Convertendo áudios"):
        result = convert_audio(f, audios_wav_dir)
        results.append(result)
    return results
