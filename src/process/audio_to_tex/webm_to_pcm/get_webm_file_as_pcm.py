from configPy import TempDirManager
from pathlib import Path
import subprocess

# deve raceber um path de um arquivo, e transformar em um arquivo .wav

def ffmpeg_convert_to_pcm(path:Path,
                          output: Path,
                          sample_rate : int = 16000,
                          channels : int = 1,
                          bytes_per_sample : int = 2
                          ) -> Path:
    
    fmt = f"s{bytes_per_sample * 8}le"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(path),
        "-ac", str(channels),
        "-ar", str(sample_rate),
        "-f", fmt,
        str(output)
    ]

    subprocess.run(cmd, check=True)
    return output

def webm_to_pcm_12b(path:Path, tempDir: TempDirManager|None = None)-> tuple[Path, TempDirManager]:
    if not tempDir:
        tempDir = TempDirManager()

    output_path = tempDir.create_file_path(path.stem, "wav")

    ffmpeg_convert_to_pcm(
            path,
            output_path,
            sample_rate=16000,
            channels=1,
            bytes_per_sample=2)

    return output_path, tempDir
