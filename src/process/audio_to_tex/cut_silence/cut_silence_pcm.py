from configPy import TempDirManager
from pathlib import Path
from .threshold import get_stream_threshold
import subprocess

def remove_silence(
    path: Path,
    tempDir: TempDirManager | None = None,
    min_silence_len: float = 1,
    remove_leading_trailing: bool = True,
    debug: bool = False
) -> tuple[Path, TempDirManager]:
    if not tempDir:
        tempDir = TempDirManager()

    # saída do arquivo cortado
    output_path = tempDir.create_file_path(path.stem + "_cut", "wav")

    # calcula thresholds
    silence, murmur = get_stream_threshold(path)
    if silence is None:
        raise ValueError(f"Não foi possível calcular threshold para {path}")

    threshold_db = silence  # usa o threshold de silêncio

    # monta parâmetros do filtro
    params = f"stop_periods=-1:stop_threshold={threshold_db}dB:stop_duration={min_silence_len}"
    if remove_leading_trailing:
        params = (
            f"start_periods=1:start_threshold={threshold_db}dB:start_duration={min_silence_len}:"
            + params
        )

    # comando ffmpeg
    cmd = [
        "ffmpeg", "-y", "-i", str(path),
        "-af", f"silenceremove={params}",
        str(output_path)
    ]

    subprocess.run(
        cmd,
        stdout=None if debug else subprocess.DEVNULL,
        stderr=None if debug else subprocess.DEVNULL,
        check=True
    )

    return output_path, tempDir
