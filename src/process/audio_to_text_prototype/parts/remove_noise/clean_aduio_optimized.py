import subprocess
import io
from configPy import Config

models_dir = Config.get_dir_noise_models()
path_rnnoise = models_dir.get_any("sh.rnnn")


def denoise_audioIO_norm(audio_buffer: io.BytesIO, sample_rate:int=16000) -> io.BytesIO:

    af_filter = f"arnndn=m={str(path_rnnoise)},loudnorm=I=-20:LRA=7:tp=-1"

    cmd = [
        "ffmpeg", "-i", "pipe:0",
        "-af", af_filter, 
        "-f", "wav",
        "-ar", str(sample_rate),
        "pipe:1"
    ]

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    data, err = proc.communicate(input=audio_buffer.read())

    if proc.returncode != 0 or not data:
        raise RuntimeError(f"Erro no denoise: {err.decode() if err else 'sem saída'}")

    audio_buffer.seek(0)
    audio_buffer.truncate(0)
    audio_buffer.write(data)
    audio_buffer.seek(0)

    return audio_buffer
