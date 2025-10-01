from pathlib import Path
import numpy as np


def get_stream_threshold(
    path: Path,
    sample_rate: int = 16000,
    channels: int = 1,
    bytes_per_sample: int = 2,
    block_size_sec: float = 0.1,
    eps: float = 1e-10,
) -> tuple[float | None, float | None]:

    block_size_bytes = int(block_size_sec * sample_rate * channels * bytes_per_sample)
    energies_db = []

    with open(path, "rb") as f:
        while True:
            raw = f.read(block_size_bytes)
            if not raw:
                break

            samples = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
            if samples.size == 0:
                continue

            rms = np.sqrt(np.mean(samples**2))
            energies_db.append(20 * np.log10(max(rms, eps)))

    if len(energies_db) == 0:
        return None, None

    energies_db = np.array(energies_db)
    silence_threshold = np.percentile(energies_db, 5)
    murmur_threshold = np.percentile(energies_db, 15)

    return silence_threshold, murmur_threshold
