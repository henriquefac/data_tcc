import subprocess
import io
from pathlib import Path


def webm_to_pcmIO(path: Path, sample_rate: int = 16000, channels = 1)->io.BytesIO:
    cmd = [
        "ffmpeg", "-i", str(path),
        "-f", "wav",
        "-acodec", "pcm_s16le",
        "-ac", str(channels),
        "-ar", str(sample_rate),
        "-hide_banner",
        "-loglevel", "error",
        "pipe:1"
    ]    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    data, _ = proc.communicate()
    return io.BytesIO(data)
    

def save_wavIO(audio: io.BytesIO, output: Path):

    with open(output, "wb") as out_file:
        audio.seek(0)
        out_file.write(audio.read())
