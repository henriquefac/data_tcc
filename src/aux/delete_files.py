from pathlib import Path
import subprocess

def rm_file(path: Path):
    try:
        subprocess.run(
            ["rm", str(path)]
        )
    except subprocess.CalledProcessError:
        return False

__all__ = ["rm_file"]
