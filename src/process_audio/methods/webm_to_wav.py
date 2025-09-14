import subprocess
from configPy import DirManager
from pathlib import Path

def webm_to_wav(input_path: Path, output_path: DirManager, sample_rate: int = 16000):
    namefile = input_path.stem
    suffix = "wav"
    wav_file = output_path.create_file_path(namefile, suffix=suffix)

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-ar", str(sample_rate), "-ac", "1",
        "-c:a", "pcm_s16le", str(wav_file)
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    return wav_file
