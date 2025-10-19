from pathlib import Path
import subprocess
import io



def preprocess_audio_ffmpeg(path:Path|str, sample_rate:int = 16000, channels: int = 1) -> io.BytesIO:
    if isinstance(path, Path):
        path = str(path)

    cmd = [
        "ffmpeg", "-i", path,
        "-f", "wav",
        "-acodec", "pcm_s16le",
        "-ac", str(channels),
        "-ar", str(sample_rate),
        "-af", "dynaudnorm=f=150:g=15,acompressor",
        "-hide_banner",
        "-loglevel", "error",
        "pipe:1"
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    data, _ = proc.communicate()

    return io.BytesIO(data)


