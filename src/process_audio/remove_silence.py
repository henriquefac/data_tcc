from configPy import Config, DirManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
from tqdm import tqdm
from pathlib import Path


files_dir = Config.get_dir_files()
videos_dir = files_dir["audios"]

# Diretório de saída para os áudios editados
audio_ed_dir = files_dir.create_dir("audio_edit")

def get_files():
    return [f[1] for f in videos_dir.list_files().items()]

def remove_silence(input_audio: Path, output_dir: DirManager, min_silence=2, silence_threshold=-30, show_log=False, to_wav=False):
    """
    Remove silêncios de um áudio.

    Args:
        input_audio (Path): Caminho do arquivo de áudio.
        output_dir (DirManager): Diretório de saída.
        min_silence (float): Duração mínima do silêncio em segundos.
        silence_threshold (float): Limite de silêncio em dB.
        show_log (bool): Se True, exibe logs do FFmpeg.
        to_wav (bool): Se True, converte o áudio de saída para WAV PCM padrão.
    """
    try:
        output_audio = output_dir.create_file_path(
            input_audio.stem,
            "wav" if to_wav else input_audio.suffix.lstrip("."),
            exist_ok=False
        )
    except:
        return "Já existe"

    # Define codec de saída
    codec = "pcm_s16le" if to_wav else "libopus"


    # Filtro atualizado para remover silencios em qualquer parte do áudio
    silenceremove_filter = (
        f"silenceremove=start_periods=1:start_duration={min_silence}:"
        f"start_threshold={silence_threshold}dB:"
        f"stop_periods=-1:stop_duration={min_silence}:stop_threshold={silence_threshold}dB:"
        f"detection=peak"
    )

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "quiet" if not show_log else "info",
        "-y",
        "-i", str(input_audio),
        "-af", silenceremove_filter,
        "-c:a", codec,
        str(output_audio)
    ]

    subprocess.run(cmd, check=True)
    return output_audio



def cut_silence_from_audio(max_workers: int = 5, min_silence=2, silence_threshold=-30, show_log=False, to_wav=False):
    all_files = get_files()
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(remove_silence, f, audio_ed_dir, min_silence, silence_threshold, show_log, to_wav): f for f in all_files}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Editando áudios"):
            audio_path = future.result()
            results.append(audio_path)


    return results
