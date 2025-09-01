from configPy import Config, DirManager

files_dir = Config.get_dir_files()
audios_dir = files_dir["audios"]

path = audios_dir["sessao-de-2-10-2023-Ata73.webm"]

import subprocess
import numpy as np

sample_rate = 16000
channels = 1
bytes_per_sample = 2
block_size_sec = 0.1
block_size_bytes = int(block_size_sec * sample_rate * channels * bytes_per_sample)

cmd = [
    "ffmpeg", "-i", path,
    "-f", "s16le", "-acodec", "pcm_s16le",
    "-ac", str(channels), "-ar", str(sample_rate), "-"
]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

energies_db = []
eps = 1e-10
while True:
    raw = proc.stdout.read(block_size_bytes)
    if not raw:
        break
    samples = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    if samples.size == 0:
        continue
    rms = np.sqrt(np.mean(samples**2))
    energies_db.append(20 * np.log10(max(rms, eps)))

energies_db = np.array(energies_db)


silence_threshold = np.percentile(energies_db, 5)
murmur_threshold = np.percentile(energies_db, 15)
print("Silêncio:", silence_threshold, "dB")
print("Murmúrios:", murmur_threshold, "dB")
