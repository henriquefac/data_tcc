from configPy import TempDirManager
from pathlib import Path
import subprocess

# deve raceber um path de um arquivo, e transformar em um arquivo .wav

def ffmpeg_convert_to_wav(
    input_path: Path,
    output_path: Path,
    sample_rate: int = 16000,
    channels: int = 1,
    bytes_per_sample: int = 2,
) -> Path:
    """
    Converte qualquer formato de áudio (ex: .webm) em um arquivo WAV PCM.

    Args:
        input_path: Caminho do arquivo de entrada.
        output_path: Caminho onde o WAV será salvo.
        sample_rate: Taxa de amostragem (Hz), padrão 16kHz.
        channels: Número de canais (1 = mono).
        bytes_per_sample: 2 → 16 bits (padrão).

    Returns:
        Path para o arquivo WAV gerado.
    """

    bit_depth = bytes_per_sample * 8
    fmt = f"pcm_s{bit_depth}le"

    cmd = [
        "ffmpeg",
        "-y",                      # sobrescreve saída
        "-i", str(input_path),     # entrada
        "-ac", str(channels),      # canais
        "-ar", str(sample_rate),   # taxa de amostragem
        "-acodec", fmt,            # codec PCM linear
        "-f", "wav",               # formato contêiner WAV
        str(output_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Erro na conversão ffmpeg:\n{e.stderr}"
        ) from e

    return output_path


def webm_to_pcm_16b(path:Path, tempDir: TempDirManager|None = None)-> tuple[Path, TempDirManager]:
    if not tempDir:
        tempDir = TempDirManager()

    output_path = tempDir.create_file_path(path.stem, "wav")

    ffmpeg_convert_to_wav(
            path,
            output_path,
            sample_rate=16000,
            channels=1,
            bytes_per_sample=2)

    return output_path, tempDir
