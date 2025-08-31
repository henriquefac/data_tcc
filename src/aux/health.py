from configPy import Config, DirManager
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
from tqdm import tqdm
import json

file_dir = Config.get_dir_files()
audio_dir = file_dir["audios"]


def get_all_files():
    return [f[1] for f in audio_dir.list_files().items()]

def check_file(audio_path: Path)-> bool:
    try:
        subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(audio_path), "-f", "null", "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )
        return (True)
    except subprocess.CalledProcessError:
        return False


def check_all_files(max_workers:int = 5):

    all_files = get_all_files()
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_file, f):f for f in all_files}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Verificando áudios"):
            if not future.result():
                results.append(str(futures[future]))
    return results

__all__ = ["check_all_files"]

if __name__ == "__main__":
    array_corrupt_paths = check_all_files(10)
    print(json.dumps(array_corrupt_paths, indent=2))
    
